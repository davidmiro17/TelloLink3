#!/usr/bin/env python3
"""
Test simple para verificar que los Mission Pads funcionan correctamente.

Requisitos:
- Tello EDU (NO funciona con Tello estándar)
- Mission pad visible bajo el dron
- Buena iluminación

Uso:
    python test_mission_pads.py
"""

import time
from TelloLink.Tello import TelloDron


def main():
    print("=" * 60)
    print("TEST MISSION PADS - TelloLink3")
    print("=" * 60)

    dron = TelloDron()

    # 1. Conectar
    print("\n[1/5] Conectando al dron...")
    try:
        dron.connect()
        print(f"✓ Conectado. Estado: {dron.state}")
    except Exception as e:
        print(f"✗ Error al conectar: {e}")
        return

    # 2. Verificar batería
    print("\n[2/5] Verificando batería...")
    time.sleep(0.5)
    try:
        bat = dron._tello.get_battery()
        print(f"✓ Batería: {bat}%")
        if bat < 20:
            print("⚠ ADVERTENCIA: Batería baja. Recomendado ≥20%")
    except Exception as e:
        print(f"⚠ No se pudo leer batería: {e}")

    # 3. Activar mission pads (sin despegar)
    print("\n[3/5] Activando mission pads...")
    try:
        result = dron.enable_mission_pads()
        if result:
            print("✓ Mission pads activados correctamente")
        else:
            print("✗ Error activando mission pads")
            print("   ¿Tienes un Tello EDU? (no funciona en Tello estándar)")
            return
    except Exception as e:
        print(f"✗ Excepción activando mission pads: {e}")
        return

    # 4. Esperar y verificar detección
    print("\n[4/5] Buscando mission pad...")
    print("   Asegúrate de que el pad esté visible bajo el dron")
    time.sleep(2)

    detected = False
    for i in range(10):
        try:
            if dron.is_mission_pad_detected():
                detected = True
                break
        except Exception:
            pass
        print(f"   Intento {i+1}/10...", end="\r")
        time.sleep(0.5)

    print()  # Nueva línea

    if not detected:
        print("✗ NO se detectó ningún mission pad")
        print("\nPosibles causas:")
        print("  - No tienes un Tello EDU (solo EDU soporta mission pads)")
        print("  - El mission pad no está visible para la cámara")
        print("  - Mala iluminación")
        print("  - El pad está demasiado lejos o inclinado")
        dron.disable_mission_pads()
        dron.disconnect()
        return

    print("✓ Mission pad detectado!")

    # 5. Leer coordenadas en bucle
    print("\n[5/5] Leyendo coordenadas del mission pad...")
    print("-" * 60)
    print("Presiona Ctrl+C para salir\n")

    try:
        while True:
            pos = dron.get_mission_pad_position()

            if pos:
                print(f"Pad ID: {pos['id']} | X: {pos['x']:6.1f} cm | Y: {pos['y']:6.1f} cm | Z: {pos['z']:6.1f} cm", end="\r")
            else:
                print("Sin detección                                                    ", end="\r")

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n\n✓ Test finalizado")

    # Cleanup
    print("\nDesconectando...")
    try:
        dron.disable_mission_pads()
        dron.disconnect()
        print("✓ Desconectado correctamente")
    except Exception as e:
        print(f"⚠ Error al desconectar: {e}")

    print("\n" + "=" * 60)
    print("FIN DEL TEST")
    print("=" * 60)


if __name__ == "__main__":
    main()
