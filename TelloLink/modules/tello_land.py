import time, threading


def _land(self, timeout_s=5):
    try: #Intenta leer la altura inicial del dron
        h0 = int(self._tello.get_height())
    except Exception:
        h0 = -1 #Si el comando no se llega a completarse
    if h0 != -1 and h0 <= 20: #Si es válida y la altura es menor a 20 cm
        print(f"Altura inicial {h0} cm. Ya está en el suelo, no mando 'land'.") #Consideramos que ya está en el suelo, ya que el sensor del Tello no es muy preciso
        self.state = "connected"
        return True

    try:
        resp = self._send("land") #Se intenta enviar el comando land al dron
    except Exception as e: #Si hay error
        try:
            h = int(self._tello.get_height()) #Intenta leer la altura del dron
        except Exception:
            h = -1 #Si tambiíen falla la lectura, se pone -1
        if h != -1 and h <= 20: #Si la lectura fue válida y el dron está a 20 cm o menos del suelo
            print(f"[WARN] 'land' lanzó excepción ({e}) pero altura={h} cm. Doy por aterrizado.") #Se da por aterrizado aunque land haya fallado, pues por telemería vemos que está en el suelo
            self.state = "connected" #Pasa a connected
            return True
        raise

    #Si la respuesta no es "ok", hay un error concreto
    if str(resp).lower() != "ok":
        #Hacemos el mismo proceso que en la función anterior
        try:
            h = int(self._tello.get_height())
        except Exception:
            h = -1
        if h != -1 and h <= 20:
            print(f"[WARN] 'land' devolvió '{resp}' pero altura={h} cm. Doy por aterrizado.")
            self.state = "connected"
            return True
        raise RuntimeError(f"land -> {resp}")


    time.sleep(timeout_s)
    self.state = "connected"
    print("Aterrizaje completado")
    return True

#Función pública de aterrizaje
def Land(self, blocking=True):
    if self.state != "flying":
        print("No se puede aterrizar: el dron no está volando.")
        return False
    #Si es bloqueante, llama a _land y espera a que complete
    if blocking:
        return _land(self)

    #Si no es bloqueante, crea un hilo paralelo
    else:
        th = threading.Thread(target=_land, args=(self,))
        th.daemon = True
        th.start()
        return True