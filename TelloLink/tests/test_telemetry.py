from TelloLink.Tello import TelloDron
import time

def main():
    print("=== Test de telemetría ===")
    dron = TelloDron()
    dron.connect()

    print("\n--> Iniciando telemetría durante 10s...")
    dron.startTelemetry()

    # bucle de lectura
    for i in range(10):
        wifi = dron.wifi if dron.wifi is not None else "N/A"
        flight_time = dron.flight_time_s if dron.flight_time_s is not None else "N/A"
        print(
            f"[{i+1}] Altura={dron.height_cm} cm | "
            f"Battery={dron.battery_pct}% | "
            f"Temp={dron.temp_c}°C | "
            f"Wifi={wifi} | "
            f"FlightTime={flight_time}s"
        )
        time.sleep(1)

    print("\n--> Parando telemetría")
    dron.stopTelemetry()
    dron.disconnect()

    print("=== Test completado ===")

if __name__ == "__main__":
    main()