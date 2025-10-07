import time, threading

def _h_cm(self) -> int:

    try:
        if hasattr(self, "_tello") and self._tello is not None: #Si Tello existe (hay objeto Tello y no es None)
            h = int(self._tello.get_height()) #Se devuelve la altura del Tello en cm al ususario
            return max(0, h) #Se devuelve h, asegurándose que nunca sea negativo (En Tello es  común que pasen este tipo de errores)
    except Exception: #Si algo falla, ignora el error.
        pass
    return int(getattr(self, "height_cm", 0)) #Si no ha conseguido obtener la altura del dron, se usa un atributo interno height_cm.


#Comprobar altura alcanzada (Tello pone 'h' en centímetros)
def _checkAltitudeReached(self, aTargetAltitude):
    target_cm = int(aTargetAltitude * 100)  # convierto objetivo a cm
    h = int(getattr(self, "height_cm", 0))  # Se lee la telemetría. Si no existe aún se devuelve 0.
    return abs(h - target_cm) <= 15 #Calcula la diferfencia absoluta entre la altura real y la objetivo. Si es menor o igual a 15 cm (tolerancia que imponemos) se considera que ha llegado a la altura

#Función para alcanzar la altitud objetivo de forma segura y controlada
def _ascend_to_target(self, aTargetAltitude): #Si no se le pasa ninguna altura objetivo, no va a hacer nada.
    if aTargetAltitude is None:
        return


    ceiling_cm = 150 #Techo de seguridad (150 cm)
    target_cm = max(0, int(aTargetAltitude * 100)) #Se convierte la altura objetivo de metros a centímetros, y se asegura que no sea negativa
    target_cm = min(target_cm, ceiling_cm) #Compara con el techo de seguridad, y lo limita

    TOL_CM   = 15 #Tolerancia de +- 15 cm. Cuando este dentro de +-15 cm de la altura objetivo, se considera que ya llegó
    MIN_STEP = 20 #Paso mínimo que acepta Tello
    MAX_STEP = 30 #Paso máximo de seguridad
    MAX_LOOPS = 20 #Evita que el dron se quede en un bucle infinito intentando subir

    h = _h_cm(self) #Llama a la función _h_cm para obtener la altura del dron
    if h <= 0: #Si la altura es 0, no se lee bien la telemetría y no se sabe donde está el dron
        print("Telemetría no disponible. No hago subida adicional.") #Se envía un mensaje al ususario y sale de la función
        return

    loops = 0 #Empieza el contador de intentos en 0
    while True:
        faltan = target_cm - h #En cada vuelta calcula cuanto falta para la altura objetivo

        if abs(faltan) <= TOL_CM: #Si lo que falta es menor a la tolerancia
            print(f"Altura objetivo alcanzada (~{h/100:.2f} m)") #Ya la da por conseguida, la convierte a metros y pone decimal de dos cifras
            break #Sale del bucle
        if faltan < MIN_STEP: #Si lo que falta es menor que el paso mínimo de Tello
            print(f"Quedan {faltan} cm (<{MIN_STEP}). Paro por límite del SDK.") #Se informa al usuario
            break #Sale del bucle

        paso = min(MAX_STEP, faltan) #Elige el tamaño del paso, el menor entre lo que falta o el maximo de Tello

        resp = self._send(f"up {paso}") #Se envía comando "up paso" al dron
        if resp != "ok": #Si la respuesta no es ok
            raise RuntimeError(f"up {paso} -> {resp}") #Da error

        prev = h #Se guarda la altura actual
        t0 = time.time() #Inicio de la ventana temporal
        subio = False #Aún no se ha observado subida
        while time.time() - t0 < 3.0: #Bucle de espera limitada a 3 segundos
            time.sleep(0.25)
            h = _h_cm(self) #Lectura de la altura de telemetría en cada iteración
            if h >= prev + 6:  #Umbral de confirmación de movimiento . Usamos 6 cm porque es suficientemente grande para que no sea ruido/saltos pequeños
                subio = True #Se confirma que ha subido
                break #Sale

        if not subio: #Si no ha subido
            print("No detecto incremento de altura tras 'up'. Aborto subida.") #Se muestra mensaje al ususario y sale del bucle
            break

        time.sleep(0.4)

        loops += 1 #Se incrementa el contador de loops cada vez que termina un ciclo de subida
        if loops >= MAX_LOOPS: #Si se ha superado el número máximo de loops
            print("Demasiados pasos. Aborto por seguridad.") #Se aborta por seguridad saliendo del bucle
            break


#Función de despegue controlado de Tello
def _takeOff(self, aTargetAltitude=None, timeout_s=15):
    print('Empezamos a despegar')
    self.state = "takingOff" #Se pasa el estado a "despegando"

    resp = self._send("takeoff") #Se envía comando de despegue al Tello
    if resp != "ok": #Si la respuesta no es ok
        print(f"[WARN] takeoff devolvió {resp}, seguimos igualmente") #Se envía mensaje al ususario pero seguimos, a veces Tello ejecuta las ordenes pese a dar mensajes no esperados

    #Confirmar que este en el aire
    airborne = False
    t0 = time.time() #Se abre la ventana temporal
    while time.time() - t0 < 5.0:           #Ventana temporal de 5 segundos para ver si se ha levantado del suelo
        try:
            h = int(self._tello.get_height()) #Se intenta obtener la altura de telemetría
            if h >= 20: #Si es mayor que 20 cm (umbral)
                airborne = True #Se confirma y sale del bucle
                break
        except Exception: #Si hay error pasa y se intenta de nuevo
            pass
        time.sleep(0.2)

    if not airborne: #Si no se confirma el despegue
        print("[ERROR] No se confirmó despegue (altura < 20 cm). Cancelo subida adicional.") #Se informa al usuario
        self.state = "connected"            # vuelve a estado conectado
        return False

    #Si ha habido exito, despega
    print('Vamos a despegar')
    self.state = "flying" #El estado cambia a "volando"
    print("Despegue completado (≈1 m)")

    #Si el dron ha completado su despegue (por defecto 1 metro), si el ususario le ha pedido una altura mayor, realiza la subida
    if aTargetAltitude is not None:
        _ascend_to_target(self, aTargetAltitude)


#Función pública de despegue
def takeOff(self, aTargetAltitude=None, blocking=True):
    print('Vamos a despegar')

    if aTargetAltitude is not None:
        aTargetAltitude = min(float(aTargetAltitude), 1.5)  #Si el ususario pide una altura destino, lo límita a 1,5 metros (por seguridad en interiores). Se puede modificar este valor.


    if self.state not in ("connected", "landing"): #Solo se puede despegar si está conectado o acaba de aterrizar
        print("No se puede despegar: estado actual =", self.state)
        return False


    #Si es blocking, llama directamente a _takeOff
    if blocking:
        _takeOff(self, aTargetAltitude)
        return True
    #Si no es blocking, crea un hilo en paralelo que ejecuta _takeoff
    else:
        th = threading.Thread(target=_takeOff, args=(self, aTargetAltitude))
        th.daemon = True
        th.start()
        return True
