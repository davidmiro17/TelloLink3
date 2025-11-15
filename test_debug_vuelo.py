#!/usr/bin/env python3
"""
Test DEBUG en VUELO - Muestra valores RAW del SDK mientras vuelas
"""

import time
from TelloLink.Tello import TelloDron

dron = TelloDron()

print("=" * 60)
print("TEST DEBUG MISSION PADS - EN VUELO")
print("=" * 60)

print("\n[1] Conectando...")
dron.connect()
print("OK")

print("\n[2] Activando mission pads...")
dron.enable_mission_pads()
print("OK")

print("\n[3] Despegando...")
dron.takeOff(0.5, blocking=True)
print("OK - En vuelo")

print("\n[4] Leyendo coordenadas en TIEMPO REAL")
print("    Mueve el dron con las flechas y observa si cambian\n")
print("-" * 60)

try:
    for i in range(60):  # 60 segundos
        # RAW del SDK
        mid = dron._tello.get_mission_pad_id()
        x_raw = dron._tello.get_mission_pad_distance_x()
        y_raw = dron._tello.get_mission_pad_distance_y()
        z_raw = dron._tello.get_mission_pad_distance_z()

        # Pose (lo que ve la demo)
        x_pose = dron.pose.x_cm if hasattr(dron, 'pose') else None
        y_pose = dron.pose.y_cm if hasattr(dron, 'pose') else None
        z_pose = dron.pose.z_cm if hasattr(dron, 'pose') else None

        print(f"[{i+1:02d}] SDK: mid={mid} x={x_raw} y={y_raw} z={z_raw} | POSE: x={x_pose:.0f} y={y_pose:.0f} z={z_pose:.0f}    ", end="\r")

        time.sleep(1)

except KeyboardInterrupt:
    print("\n\nTest interrumpido")

print("\n\n[5] Aterrizando...")
dron.Land(blocking=False)
time.sleep(3)

print("\n[6] Desconectando...")
dron.disable_mission_pads()
dron.disconnect()
print("FIN")
