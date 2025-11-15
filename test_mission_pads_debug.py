#!/usr/bin/env python3
"""
Test DEBUG para mission pads - Muestra valores RAW del SDK
"""

import time
from TelloLink.Tello import TelloDron


def main():
    print("=" * 60)
    print("TEST DEBUG MISSION PADS")
    print("=" * 60)

    dron = TelloDron()

    # Conectar
    print("\n[1] Conectando...")
    try:
        dron.connect()
        print(f"✓ Conectado")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Activar mission pads
    print("\n[2] Activando mission pads...")
    try:
        result = dron.enable_mission_pads()
        print(f"✓ Activado: {result}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    print("\n[3] LEVANTA EL DRON 20-30cm del suelo (manualmente)")
    print("    Esperando 3 segundos...")
    time.sleep(3)

    print("\n[4] Leyendo valores RAW del SDK...")
    print("-" * 60)
    print("Presiona Ctrl+C para salir\n")

    try:
        count = 0
        while True:
            count += 1

            # Leer valores individuales RAW
            try:
                mid = dron._tello.get_mission_pad_id()
            except Exception as e:
                mid = f"ERROR: {e}"

            try:
                x = dron._tello.get_mission_pad_distance_x()
            except Exception as e:
                x = f"ERROR: {e}"

            try:
                y = dron._tello.get_mission_pad_distance_y()
            except Exception as e:
                y = f"ERROR: {e}"

            try:
                z = dron._tello.get_mission_pad_distance_z()
            except Exception as e:
                z = f"ERROR: {e}"

            # Mostrar valores RAW
            print(f"[{count:03d}] RAW → mid={mid} | x={x} | y={y} | z={z}                    ", end="\r")

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n\n✓ Test finalizado")

    # Cleanup
    print("\nDesconectando...")
    try:
        dron.disable_mission_pads()
        dron.disconnect()
        print("✓ Desconectado")
    except Exception as e:
        print(f"⚠ Error: {e}")


if __name__ == "__main__":
    main()
