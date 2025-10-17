import math
from dataclasses import dataclass

#Función para mantener siempre el ángulo entre 0 y 360 grados
def _wrap_deg(deg: float) -> float:

    d = deg % 360.0
    return d if d >= 0 else d + 360.0



@dataclass
class PoseVirtual:
    x_cm: float = 0.0
    y_cm: float = 0.0
    z_cm: float = 0.0
    yaw_deg: float = 0.0



    #Métodos básicos
    def reset(self) -> None:
        #Reinicia la pose al origen (punto de despegue).
        self.x_cm = 0.0
        self.y_cm = 0.0
        self.z_cm = 0.0
        self.yaw_deg = 0.0

    def capture(self) -> dict:
        #Devuelve la pose actual y se redondea a un decimal
        return {
            "x_cm": round(self.x_cm, 1),
            "y_cm": round(self.y_cm, 1),
            "z_cm": round(self.z_cm, 1),
            "yaw_deg": round(self.yaw_deg, 1),
        }



    def set_from_telemetry(self, height_cm: float | None = None,
                           yaw_deg: float | None = None) -> None:


        if height_cm is not None:
            self.z_cm = float(height_cm)
        if yaw_deg is not None:
            self.yaw_deg = _wrap_deg(float(yaw_deg))

    def update_yaw(self, delta_deg: float) -> None:

        self.yaw_deg = _wrap_deg(self.yaw_deg + float(delta_deg))

    def update_move(self, direction: str, dist_cm: float) -> None:

        d = float(dist_cm)
        yaw = math.radians(self.yaw_deg)

        if direction == "forward":
            self.x_cm += d * math.cos(yaw)
            self.y_cm += d * math.sin(yaw)

        elif direction == "back":
            self.x_cm -= d * math.cos(yaw)
            self.y_cm -= d * math.sin(yaw)

        elif direction == "right":
            self.x_cm -= d * math.sin(yaw)
            self.y_cm += d * math.cos(yaw)

        elif direction == "left":
            self.x_cm += d * math.sin(yaw)
            self.y_cm -= d * math.cos(yaw)

        elif direction == "up":
            self.z_cm += d

        elif direction == "down":
            self.z_cm -= d

    #Distancia entre una pose y otra
    def distance_to(self, other: "PoseVirtual") -> float:

        dx = self.x_cm - other.x_cm
        dy = self.y_cm - other.y_cm
        dz = self.z_cm - other.z_cm
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def __repr__(self) -> str:
        return (f"PoseVirtual(x={self.x_cm:.1f}, y={self.y_cm:.1f}, "
                f"z={self.z_cm:.1f}, yaw={self.yaw_deg:.1f})")