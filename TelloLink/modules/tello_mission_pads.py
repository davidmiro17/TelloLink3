"""
Módulo para interactuar con Mission Pads del Tello EDU.

Los Mission Pads son marcadores físicos que permiten al dron obtener
su posición real en 3D mediante visión por computadora.
"""

# Direcciones de detección de mission pads
DIRECTION_DOWN = 0      # Detectar solo mirando hacia abajo
DIRECTION_FORWARD = 1   # Detectar solo mirando hacia adelante
DIRECTION_BOTH = 2      # Detectar en ambas direcciones


def enable_mission_pads(self, direction=DIRECTION_DOWN):
    """
    Activa la detección de mission pads.

    Args:
        direction: DIRECTION_DOWN (0), DIRECTION_FORWARD (1), o DIRECTION_BOTH (2)

    Returns:
        True si se activó correctamente, False en caso contrario
    """
    try:
        # Activar mission pads
        resp = self._send("mon")
        if not resp or "ok" not in resp.lower():
            print(f"[mission_pads] Error activando: {resp}")
            return False

        # Configurar dirección de detección
        resp_dir = self._send(f"mdirection {direction}")
        if not resp_dir or "ok" not in resp_dir.lower():
            print(f"[mission_pads] Error configurando dirección: {resp_dir}")
            return False

        self._mission_pads_enabled = True
        print(f"[mission_pads] Activado correctamente (dirección={direction})")
        return True

    except Exception as e:
        print(f"[mission_pads] Error en enable_mission_pads: {e}")
        return False


def disable_mission_pads(self):
    """
    Desactiva la detección de mission pads.

    Returns:
        True si se desactivó correctamente, False en caso contrario
    """
    try:
        resp = self._send("moff")
        self._mission_pads_enabled = False
        print("[mission_pads] Desactivado")
        return resp and "ok" in resp.lower()

    except Exception as e:
        print(f"[mission_pads] Error en disable_mission_pads: {e}")
        return False


def get_mission_pad_id(self):
    """
    Obtiene el ID del mission pad actualmente detectado.

    Returns:
        int: ID del pad (1-8) o -1 si no hay pad detectado
    """
    try:
        mid = self._tello.get_mission_pad_id()
        return int(mid) if mid is not None and mid >= 0 else -1
    except Exception:
        return -1


def get_mission_pad_distance_x(self):
    """
    Obtiene la distancia X al mission pad (en cm).

    Sistema de coordenadas del pad:
    - Centro del pad = origen (0, 0, 0)
    - X positivo = dirección del cohete impreso en el pad

    Returns:
        float: Distancia X en cm, o -1 si no disponible
    """
    try:
        x = self._tello.get_mission_pad_distance_x()
        return float(x) if x is not None and x >= 0 else -1.0
    except Exception:
        return -1.0


def get_mission_pad_distance_y(self):
    """
    Obtiene la distancia Y al mission pad (en cm).

    Sistema de coordenadas del pad:
    - Y positivo = perpendicular a X en el plano del pad

    Returns:
        float: Distancia Y en cm, o -1 si no disponible
    """
    try:
        y = self._tello.get_mission_pad_distance_y()
        return float(y) if y is not None and y >= 0 else -1.0
    except Exception:
        return -1.0


def get_mission_pad_distance_z(self):
    """
    Obtiene la distancia Z al mission pad (altura sobre el pad, en cm).

    Returns:
        float: Altura en cm, o -1 si no disponible
    """
    try:
        z = self._tello.get_mission_pad_distance_z()
        return float(z) if z is not None and z >= 0 else -1.0
    except Exception:
        return -1.0


def is_mission_pad_detected(self):
    """
    Verifica si hay un mission pad detectado actualmente.

    Returns:
        bool: True si hay un pad detectado, False en caso contrario
    """
    try:
        mid = self._tello.get_mission_pad_id()
        return mid is not None and mid >= 1 and mid <= 8
    except Exception:
        return False


def get_mission_pad_position(self):
    """
    Obtiene la posición completa respecto al mission pad detectado.

    Returns:
        dict: {"id": int, "x": float, "y": float, "z": float} o None si no hay pad
    """
    try:
        mid = get_mission_pad_id(self)
        if mid == -1:
            return None

        x = get_mission_pad_distance_x(self)
        y = get_mission_pad_distance_y(self)
        z = get_mission_pad_distance_z(self)

        if x >= 0 and y >= 0 and z >= 0:
            return {
                "id": mid,
                "x": x,
                "y": y,
                "z": z
            }
        return None

    except Exception as e:
        print(f"[mission_pads] Error en get_mission_pad_position: {e}")
        return None
