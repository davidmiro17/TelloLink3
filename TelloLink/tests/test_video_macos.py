from TelloLink.Tello import TelloDron

def main():
    print("=== FPV en vivo (macOS, bloqueante) ===")
    dron = TelloDron()
    dron.connect()
    try:
        print("--> Mostrando FPV (cierra con 'q')...")
        # En mac usa la variante en el hilo principal
        dron.show_video_blocking(resize=(640, 360), window_name="Tello FPV")
    finally:
        try:
            # si tienes stream_off en tello_camera, apaga la cámara
            dron.stream_off()
        except Exception:
            pass
        dron.disconnect()
        print("=== Fin ===")

if __name__ == "__main__":
    main()