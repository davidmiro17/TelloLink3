from TelloLink.Tello import TelloDron
import time

def main():
    print("Test de cámara (snapshot)")
    dron = TelloDron()
    dron.connect()

    print("\n--> Encendiendo stream de vídeo")
    dron.stream_on()
    time.sleep(2)

    print("\n--> Capturando snapshot")
    try:
        path = dron.snapshot()
        print(f"✅ Foto guardada en: {path}")
    except Exception as e:
        print("Error al hacer snapshot:", e)

    print("\n--> Apagando stream")
    dron.stream_off()

    dron.disconnect()
    print("Test completado")

if __name__ == "__main__":
    main()