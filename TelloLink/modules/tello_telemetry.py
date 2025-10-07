import threading, time

def _telemetry_loop(self, period_s: float):   #Función que actualiza altura, batería, temp, calidad wifi y tiempo de vuelo.

    while not getattr(self, "_telemetry_stop", True):

        if getattr(self, "_tello", None) is None or self.state == "disconnected":    # Si Tello desconectado, no intenta leer telemetría, espera un periodo y vuelve a probar
            time.sleep(period_s)
            continue

        # Altura (cm)
        try:
            h = self._tello.get_height()
            if h is not None:
                self.height_cm = max(0, int(h))   #Si la altura existe, la guarda como entero no negativo
        except Exception:    #Si no, se ignora para que el programa no falle
            pass

        # Batería (%)
        try:
            b = self._tello.get_battery()
            if b is not None:
                self.battery_pct = max(0, int(b))   #Hacemos lo mismo
        except Exception:
            pass

        # Temperatura (°C)
        try:
            t = self._tello.get_temperature()
            if t is not None:
                self.temp_c = float(t)   #Se guarda la temperatura
        except Exception:
            pass

        # WiFi (calidad 0..100 aprox)
        try:
            w = self._tello.get_wifi()
            if w is not None:
                self.wifi = int(w)
        except Exception:
            pass

        # Tiempo de vuelo (s) (en segundos desde el despegue)
        try:
            ft = self._tello.get_flight_time()
            if ft is not None:
                self.flight_time_s = max(0, int(ft))
        except Exception:
            pass

        #Aqui se guarda la hora de la ultima lectura de la telemetría (para saber si se ha quedado "colgada" la telemetría)
        self.telemetry_ts = time.time()

        time.sleep(period_s)

def startTelemetry(self, freq_hz: int = 5):   #Función para empezar la recogida periódica de la telemetría, con un periódo de 5 lecturas por segundo

    if freq_hz <= 0: freq_hz = 5
    if getattr(self, "_telemetry_thread", None) and self._telemetry_thread.is_alive(): #Si ya hay un hilo de telemetría activo, no se arranca otro
        return False

    # Inicializa los atributos por defecto (por si no existen aún)

    self.height_cm = getattr(self, "height_cm", 0)
    self.battery_pct = getattr(self, "battery_pct", None)
    self.temp_c = getattr(self, "temp_c", None)
    self.wifi = getattr(self, "wifi", None)
    self.flight_time_s = getattr(self, "flight_time_s", 0)
    self.telemetry_ts = time.time()

    self._telemetry_stop = False
    period_s = 1.0 / float(freq_hz) #Se calcula el periodo a partir de la frecuencia

    th = threading.Thread(target=_telemetry_loop, args=(self, period_s), daemon=True) #Creamos el hilo que ejecutará _telemetry_loop
    self._telemetry_thread = th
    th.start()
    return True

def stopTelemetry(self):   #Función que detiene el hilo de telemetría si está activo.

    self._telemetry_stop = True
    th = getattr(self, "_telemetry_thread", None)
    if th and th.is_alive():
        th.join(timeout=2.0)
    self._telemetry_thread = None
    return True