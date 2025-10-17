from __future__ import annotations
import math
import threading
import time
from typing import List, Tuple, Optional, Dict, Any


# Parámetros por defecto del "cubo imaginario" (inclusión)
_DEFAULT_MAX_X_CM = 150.0   #el dron puede moverse ±1.5 m a derecha/izquierda
_DEFAULT_MAX_Y_CM = 150.0   #el dron puede moverse ±1.5 m hacia adelante/atrás
_DEFAULT_MAX_Z_CM = 120.0   # el dron puede subir hasta 1.2 m

_DEFAULT_POLL_S  = 0.10     #cada cuanto tiempo comprueba que no haya violación del geofence
_HARD_LAND_DELAY = 0.0      #espera antes de Land en modo "hard"

#Acción al violar geofence
MODE_SOFT_ABORT = "soft"    # aborta goto/mission actual del dron (dron se queda quieto en el aire)
MODE_HARD_LAND  = "hard"    # aterriza inmediatamente, sin esperar a que termine ninguna acción



def _point_in_poly(x: float, y: float, poly: List[Tuple[float, float]]) -> bool: #Sirve para comprobar la posición del dron respecto a una zona poligonal (zona de exclusión)
    inside = False #Inicialmente se supone que el punto está fuera del polígono
    n = len(poly) #Cualquier polígono necesita almenos 3 puntos (triángulo), si hay menos, no comprueba nada
    if n < 3:
        return False
    j = n - 1  #guarda el índice del último vértice
    for i in range(n): #recorre cada borde del polígono. i es el vértice actual, j es el vértice anterior
        xi, yi = poly[i]
        xj, yj = poly[j]
        cond = ((yi > y) != (yj > y)) # detecta si el borde del polígono pasa por la altura (Y) del dron
        if cond: #Si se cruza horizontalmente la altura del dron
            # evitar división por 0 en aristas horizontales
            denom = (yj - yi) if (yj - yi) != 0 else 1e-9  #Diferencia vertical entre los vértices; evita dividir por 0 si el borde es horizontal
            x_inter = (xj - xi) * (y - yi) / denom + xi  #Calcula la coordenada X donde el borde del polígono cruza la línea horizontal del dron (Y=y)
            if x < x_inter: #Si el punto del dron está a la izquierda del cruce del borde con la línea horizontal
                inside = not inside  #Cambia el estado (de fuera a dentro, o de dentro a fuera)
        j = i #Avanza: el vértice actual pasa a ser el anterior para la próxima iteración
    return inside # Devuelve True si el número de cruces fue impar (dron dentro del polígono)

#Función que devuelve true si el punto (x,y) está dentro o sobre un círculo
def _point_in_circle(x: float, y: float, cx: float, cy: float, r_cm: float) -> bool:
    #Calcula cuanto se separa del centro el punto en cada eje
    dx = x - cx
    dy = y - cy
    return (dx * dx + dy * dy) <= (r_cm * r_cm) #Devuelve true si el punto está dentro del círculo o en el borde



# API pública

def set_geofence(self,
                 max_x_cm: float = _DEFAULT_MAX_X_CM,
                 max_y_cm: float = _DEFAULT_MAX_Y_CM,
                 max_z_cm: float = _DEFAULT_MAX_Z_CM,
                 mode: str = MODE_SOFT_ABORT,
                 poll_interval_s: float = _DEFAULT_POLL_S) -> None:
    # Almacenar límites y estado
    self._gf_limits = {
        "max_x": float(max_x_cm),
        "max_y": float(max_y_cm),
        "max_z": float(max_z_cm),
    }
    self._gf_mode = mode if mode in (MODE_SOFT_ABORT, MODE_HARD_LAND) else MODE_SOFT_ABORT
    self._gf_poll_s = max(0.03, float(poll_interval_s))

    #Si todavía no existen las listas de zonas de exclusión las crea
    if not hasattr(self, "_gf_excl_polys"):
        self._gf_excl_polys: List[List[Tuple[float, float]]] = []
    if not hasattr(self, "_gf_excl_circles"):
        self._gf_excl_circles: List[Tuple[float, float, float]] = []

    #Flags que indican que la geofence está activa y que el hilo debe correr
    self._gf_enabled = True
    self._gf_monitoring = True

    # Si ya había un hilo de geofence, lo detiene de forma segura
    if hasattr(self, "_gf_thread") and getattr(self, "_gf_thread"):
        try:
            self._gf_monitoring = False
            self._gf_thread.join(timeout=1.0)
        except Exception:
            pass

    # Arrancar monitor, que revisa constantemente la posición del dron
    t = threading.Thread(target=_gf_monitor_loop, args=(self,), daemon=True)
    self._gf_thread = t
    t.start()

#Detiene el geofence pero no elimina las zonas configuradas
def disable_geofence(self) -> None:
    self._gf_enabled = False
    self._gf_monitoring = False
    t = getattr(self, "_gf_thread", None)
    if t and isinstance(t, threading.Thread):
        try:
            t.join(timeout=1.0)
        except Exception:
            pass
    self._gf_thread = None
    print("[geofence] Desactivada.")


#Función para añadir polígonos de exclusión
def add_exclusion_poly(self, points_cm: List[Tuple[float, float]]) -> List[Tuple[float, float]]:

    if not hasattr(self, "_gf_excl_polys"): #Si aún no tiene una lista de polígonos de exclusión, la crea vacía
        self._gf_excl_polys = []
    self._gf_excl_polys.append([ (float(x), float(y)) for (x,y) in points_cm ]) #Añade el nuevo polígono a la lista general de exclusiones
    return self._gf_excl_polys[-1]

#Función para añadir directamente rectángulos de exclusión
def add_exclusion_rect(self, x_min_cm: float, y_min_cm: float,
                       size_x_cm: float, size_y_cm: float) -> List[Tuple[float, float]]:

    x0, y0 = float(x_min_cm), float(y_min_cm) #Guarda los valores iniciales de la esquina inferior izquierda
    sx, sy = abs(float(size_x_cm)), abs(float(size_y_cm)) #Calcula el tamaño de cada eje
    poly = [(x0, y0), (x0+sx, y0), (x0+sx, y0+sy), (x0, y0+sy)] #Construye una lista de cuatro puntos (vértices) que forman el rectángulo
    return add_exclusion_poly(self, poly) #Se registra como un polígono de exclusión

#Función para añadir circulos de exclusión
def add_exclusion_circle(self, cx_cm: float, cy_cm: float, radius_cm: float) -> Tuple[float, float, float]:
    if not hasattr(self, "_gf_excl_circles"): #Si aún no tiene una lista de círculos de exclusión, la crea vacía
        self._gf_excl_circles = []
    c = (float(cx_cm), float(cy_cm), abs(float(radius_cm))) #Crea una tupla c que representa el círculo
    self._gf_excl_circles.append(c) #Añade el círculo a las zonas de exclusión
    return c

#Función para consultar las zonas de exclusión activas
def get_exclusions(self) -> Dict[str, Any]:
    return {
        "polys": list(getattr(self, "_gf_excl_polys", [])),
        "circles": list(getattr(self, "_gf_excl_circles", [])),
    }

#Función para eliminar todas las zonas de exclusión registradas
def clear_exclusions(self) -> None:
    """Elimina todas las exclusiones (polígonos y círculos)."""
    self._gf_excl_polys = []
    self._gf_excl_circles = []


#Comprueba si una posición determinada está permitida según inclusión/exclusión
def check_position_allowed(self, x_cm: float, y_cm: float, z_cm: float) -> bool:
    if not _inside_inclusion(self, x_cm, y_cm, z_cm):
        return False
    if _inside_any_exclusion(self, x_cm, y_cm):
        return False
    return True

# Lógica del monitor
def _gf_monitor_loop(self) -> None:
    print("[geofence] Monitor iniciado.")
    while getattr(self, "_gf_monitoring", False) and getattr(self, "_gf_enabled", False):
        try:
            # Requisitos mínimos. Si el dron no está volando ni aterrizando, no vigila.
            if getattr(self, "state", "") not in ("flying", "landing"):
                time.sleep(self._gf_poll_s)
                continue
            #Se necesita la pose virtual para poner x,y,z. Si no existe aún, espera y reintenta.
            pose = getattr(self, "pose", None)
            if pose is None:
                time.sleep(self._gf_poll_s)
                continue
            #Lee coordenadas locales del dron
            x = float(getattr(pose, "x_cm", 0.0) or 0.0)
            y = float(getattr(pose, "y_cm", 0.0) or 0.0)
            z = float(getattr(pose, "z_cm", 0.0) or 0.0)

            # Caso 1) Inclusión, si está fuera, sale del bucle
            if not _inside_inclusion(self, x, y, z):
                _handle_violation(self, reason="inclusion")
                break

            # Caso 2) Exclusión 2D (XY), si está dentro, sale del bucle
            if _inside_any_exclusion(self, x, y):
                _handle_violation(self, reason="exclusion")
                break

        except Exception as e:
            print(f"[geofence] Error en monitor: {e}")
            #Cualquier error puntual no hace parar el hilo

        time.sleep(getattr(self, "_gf_poll_s", _DEFAULT_POLL_S))

    print("[geofence] Monitor detenido.")

#Comprueba si el dron está dentro de la zona de inclusión
def _inside_inclusion(self, x: float, y: float, z: float) -> bool:
    lim = getattr(self, "_gf_limits", None)
    if not lim:
        return True
    if abs(x) > lim["max_x"]:
        return False
    if abs(y) > lim["max_y"]:
        return False
    if z < 0.0 or z > lim["max_z"]:
        return False
    return True

#Comprueba si el dron ha entrado en una zona de exclusión
def _inside_any_exclusion(self, x: float, y: float) -> bool:
    # Polígonos
    polys = list(getattr(self, "_gf_excl_polys", []))
    for poly in polys:
        if _point_in_poly(x, y, poly):
            return True
    # Círculos
    circles = list(getattr(self, "_gf_excl_circles", []))
    for cx, cy, r in circles:
        if _point_in_circle(x, y, cx, cy, r):
            return True
    return False

#Función que se llama cuando se detecta una violación
def _handle_violation(self, reason: str) -> None:
    mode = getattr(self, "_gf_mode", MODE_SOFT_ABORT)
    print(f"[geofence] Violación ({reason}). Modo='{mode}'.")

    # Señales para cortar movimientos/mission en curso
    try:
        setattr(self, "_goto_abort", True)
        setattr(self, "_mission_abort", True)
    except Exception:
        pass

    if mode == MODE_HARD_LAND:
        # Aterrizaje de emergencia
        try:
            if _HARD_LAND_DELAY > 0:
                time.sleep(_HARD_LAND_DELAY)
            self.Land(blocking=True)
        except Exception as e:
            print(f"[geofence] Error aterrizando: {e}")
    else:
        # Modo "soft"
        pass

    # Detener monitor (evitar spam/land repetidos)
    try:
        self._gf_monitoring = False
    except Exception:
        pass
