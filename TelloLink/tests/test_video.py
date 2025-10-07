# tests/test_video.py
from TelloLink.Tello import TelloDron
import time

def main():
    print("Test de vídeo FPV")
    dron = TelloDron()
    dron.connect()

    print("\n--> Iniciando ventana de vídeo")
    dron.start_video(resize=(640, 480), window_name="Tello FPV")

    # Mantener ventana durante 10 segundos
    for i in range(10):
        print(f"[{i+1}] Ventana activa...")
        time.sleep(1)

    print("\n--> Parando vídeo")
    dron.stop_video()
    dron.disconnect()
    print("Test completado")









if __name__ == "__main__":
    main()