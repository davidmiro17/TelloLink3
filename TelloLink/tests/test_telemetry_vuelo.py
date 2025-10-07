from TelloLink.Tello import TelloDron
import time

def main():
    print("Test de telemetría con vuelo corto y seguro (indoor)")
    dron = TelloDron()
    dron.connect()
    time.sleep(2)  #pausa pequeña

    #Telemetría
    dron.startTelemetry(freq_hz=5)
    time.sleep(1)  # deja que lleguen primeras lecturas

    #Lectura inicial (con N/A donde falte)
    wifi = dron.wifi if dron.wifi is not None else "N/A"
    bat  = dron.battery_pct if dron.battery_pct is not None else "N/A"
    temp = dron.temp_c if dron.temp_c is not None else "N/A"
    print(f"Inicial -> Altura={dron.height_cm} cm | Battery={bat}% | Temp={temp}°C | Wifi={wifi} | FlightTime={dron.flight_time_s}s")

    #Safety: batería mínima (20%)
    if isinstance(dron.battery_pct, int) and dron.battery_pct < 20: #Si el valor es entero y menor de 20 (el porcentaje)
        print("Batería baja (<20%). Abortando prueba por seguridad.")
        dron.stopTelemetry()
        dron.disconnect()
        return

    #Vuelo corto: despegue bajo y mantener 5
    target_m = 1.0  # objetivo conservador (capado internamente a 1.5 m)
    print(f"\n--> Despegando a {target_m} m (indoor)")
    took_off = False

    try:
        # Despegue (bloqueante)
        ok = dron.takeOff(target_m, blocking=True)
        if not ok:
            print("No se pudo iniciar el despegue (estado no válido).")
            return
        took_off = True

        # Ventana de observación en el aire (5 s)
        print("\n--> Telemetría en aire (5 s):")
        t0 = time.time()
        while time.time() - t0 < 5.0:
            wifi = dron.wifi if dron.wifi is not None else "N/A"
            flight_time = dron.flight_time_s if dron.flight_time_s is not None else "N/A"
            temp = dron.temp_c if dron.temp_c is not None else "N/A"
            print(
                f"Altura={dron.height_cm} cm | "
                f"Battery={dron.battery_pct}% | "
                f"Temp={temp}°C | "
                f"Wifi={wifi} | "
                f"FlightTime={flight_time}s"
            )
            time.sleep(0.5)

        # Aterrizaje
        print("\n--> Aterrizando...")
        dron.Land(blocking=True)

    finally:
        # Si algo falló, intenta aterrizar igualmente
        if took_off and dron.state != "connected":
            try:
                dron.Land(blocking=True)
            except Exception:
                pass
        # Cierre limpio de telemetría y conexión
        try:
            dron.stopTelemetry()
        except Exception:
            pass
        try:
            dron.disconnect()
        except Exception:
            pass

    print("\n=== Test completado ===")

if __name__ == "__main__":
    main()