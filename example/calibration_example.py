import numpy as np
from calibration import (ChessboardCalibrator, 
                        CircleGridCalibrator, 
                        ArucoBoardCalibrator,
                        CharucoBoardCalibrator)
from typing import Tuple, List

def generate_gripper_positions(
    num_positions: int = 10,
    x_limits: Tuple[float, float] = (0.0, 1.0),
    y_limits: Tuple[float, float] = (0.0, 1.0),
    z_limits: Tuple[float, float] = (0.0, 1.0),
    roll_limits: Tuple[float, float] = (-np.pi/4, np.pi/4),
    pitch_limits: Tuple[float, float] = (-np.pi/4, np.pi/4),
    yaw_limits: Tuple[float, float] = (-np.pi/2, np.pi/2),
    seed: int = None
) -> List[Tuple[float, float, float, float, float, float]]:
    """
    Генерирует список случайных позиций gripper в заданных пределах
    
    Args:
        num_positions: Количество генерируемых позиций
        x_limits: (min, max) по оси X (метры)
        y_limits: (min, max) по оси Y (метры)
        z_limits: (min, max) по оси Z (метры)
        roll_limits: (min, max) для крена (радианы)
        pitch_limits: (min, max) для тангажа (радианы)
        yaw_limits: (min, max) для рысканья (радианы)
        seed: Seed для генератора случайных чисел
        
    Returns:
        Список кортежей (x, y, z, roll, pitch, yaw)
    """
    if seed is not None:
        np.random.seed(seed)
    
    positions = []
    for _ in range(num_positions):
        x = np.random.uniform(*x_limits)
        y = np.random.uniform(*y_limits)
        z = np.random.uniform(*z_limits)
        roll = np.random.uniform(*roll_limits)
        pitch = np.random.uniform(*pitch_limits)
        yaw = np.random.uniform(*yaw_limits)
        
        positions.append((x, y, z, roll, pitch, yaw))
    
    return positions


checker_folder = "/home/daniel/dev/docker_dev/web_service/calibration_module/images/checker"
circle_async_folder = "/home/daniel/dev/docker_dev/web_service/calibration_module/images/circle_async"
circle_sync_folder = "/home/daniel/dev/docker_dev/web_service/calibration_module/images/circle_sync"
aruco_folder = "/home/daniel/dev/docker_dev/web_service/calibration_module/images/aruco"
charuco_folder = "/home/daniel/dev/docker_dev/web_service/calibration_module/images/handeye"


pattern_size = (5, 7)
square_length_mm = 40
marker_length_mm = 25


chessboard_calibrator = ChessboardCalibrator(image_folder=checker_folder,
                                            pattern_size=(4, 6),
                                            pattern_length_mm=square_length_mm)

circle_asym_calibrator = CircleGridCalibrator(image_folder=circle_async_folder,
                                             pattern_size=(5, 4),
                                             pattern_length_mm=square_length_mm,
                                             asymmetric=True)
    
circle_sym_calibrator = CircleGridCalibrator(image_folder=circle_sync_folder,
                                             pattern_size=pattern_size,
                                             pattern_length_mm=square_length_mm,
                                             asymmetric=False)

aruco_calibrator = ArucoBoardCalibrator(image_folder=aruco_folder,
                                       pattern_size=pattern_size,
                                       aruco_dict_name="4x4_50",
                                       marker_length_mm=square_length_mm,
                                       marker_separation=0.25)

charuco_calibrator = CharucoBoardCalibrator(image_folder=charuco_folder,
                                           pattern_size=pattern_size,
                                           aruco_dict_name="4x4_50",
                                           pattern_length_mm=55,
                                           marker_length_mm=40)


print("Chessboard калибровка")
try:
    chessboard_result = chessboard_calibrator.calibrate(pattern="*.jpg")
    # chessboard_calibrator.save_calibration_result(output_path="./chessboard.npz")
    print("Точность калибровки:", chessboard_result["ret"])
    print("Матрица камеры:", chessboard_result["matrix"].tolist())
    print("Дисторсия:", chessboard_result["distortion"])
except Exception as e:
    print(e)
print()

print("Circle asym калибровка")
try:
    circle_async_result = circle_asym_calibrator.calibrate(pattern="*.jpg")
    print("Точность калибровки:", circle_async_result["ret"])
    print("Матрица камеры:", circle_async_result["matrix"].tolist())
    print("Дисторсия:", circle_async_result["distortion"])
except Exception as e:
    print(e)
print()

print("Circle sym калибровка")
try:
    circle_sync_result = circle_sym_calibrator.calibrate(pattern="*.jpg")
    print("Точность калибровки:", circle_sync_result["ret"])
    print("Матрица камеры:", circle_sync_result["matrix"].tolist())
    print("Дисторсия:", circle_sync_result["distortion"])
except Exception as e:
    print(e)
print()

print("Aruco калибровка")
try:
    aruco_result = aruco_calibrator.calibrate(pattern="*.jpg")
    # aruco_calibrator.save_calibration_result(output_path="./aruco.txt")
    print("Точность калибровки:", aruco_result["ret"])
    print("Матрица камеры:", aruco_result["matrix"].tolist())
    print("Дисторсия:", aruco_result["distortion"])
except Exception as e:
    print(e)
print()

print("Charuco калибровка")
try:
    charuco_result = charuco_calibrator.calibrate(pattern="*.jpg")
    charuco_calibrator.save_calibration_result(output_path="./charuco.npz")
    charuco_result = charuco_calibrator.load_calibration_result("./charuco.npz")
    print("Точность калибровки:", charuco_result["ret"])
    print("Матрица камеры:", charuco_result["matrix"].tolist())
    print("Дисторсия:", charuco_result["distortion"])
except Exception as e:
    print(e)
print()
 

print("Charuco handeye калибровка")
gripper_positions = generate_gripper_positions(
    num_positions=20,
    x_limits=(0.05, 0.15),    # X от 5см до 15см
    y_limits=(0.15, 0.25),    # Y от 15см до 25см
    z_limits=(0.25, 0.35),    # Z от 25см до 35см
    roll_limits=(0.0, 0.2),   # Roll от 0 до 0.2 рад (~11.5°)
    pitch_limits=(-0.1, 0.1), # Pitch от -0.1 до 0.1 рад (~±5.7°)
    yaw_limits=(0.1, 0.3),    # Yaw от 0.1 до 0.3 рад (~5.7°-17.2°)
    seed=42  # Фиксированный seed для воспроизводимости
)

gripper_positions = [
    (430/1000, -0.03/1000, 645/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #21
    (556/1000, 7.77/1000, 509/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #22
    (446/1000, 7.78/1000, 509/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #23
    (552/1000, 65.42/1000, 509/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #24
    (464/1000, -131/1000, 509/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #25
    (464/1000, 48/1000, 509/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #26
    (567/1000, 48/1000, 509/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #27
    (567/1000, -123/1000, 508/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #28
    (567/1000, -59/1000, 467/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #29
    (567/1000, 20/1000, 467/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #30
    (462/1000, 20/1000, 467/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #31
    (462/1000, -88/1000, 467/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #32
    (462/1000, -88/1000, 467/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #33
    (462/1000, -192/1000, 614/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #34
    (462/1000, 143/1000, 614/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #35
    (462/1000, -46/1000, 614/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #36
    (525/1000, -46/1000, 614/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #37
    (389/1000, -46/1000, 614/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #38
    (389/1000, -173/1000, 614/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #39
    (389/1000, 102/1000, 614/1000, np.deg2rad(180), np.deg2rad(-25.28), np.deg2rad(-180)), #40
]

charuco_calibrator.image_folder = "./images/handeye"
charuco_calibrator.load_calibration_result("./charuco.npz")
R_cam2gripper, t_cam2gripper = charuco_calibrator.handeye_calibrate(gripper_poses=gripper_positions,
                                                                    pattern="*.jpg")

print("Матрица вращения (камера -> gripper):\n", R_cam2gripper)
print("Вектор перемещения (камера -> gripper):\n", t_cam2gripper)
print("Determinant R:", np.linalg.det(R_cam2gripper))
print()

print("Aruco handeye калибровка")
gripper_positions = generate_gripper_positions(
    num_positions=10,
    x_limits=(0.05, 0.15),    # X от 5см до 15см
    y_limits=(0.15, 0.25),    # Y от 15см до 25см
    z_limits=(0.25, 0.35),    # Z от 25см до 35см
    roll_limits=(0.0, 0.2),   # Roll от 0 до 0.2 рад (~11.5°)
    pitch_limits=(-0.1, 0.1), # Pitch от -0.1 до 0.1 рад (~±5.7°)
    yaw_limits=(0.1, 0.3),    # Yaw от 0.1 до 0.3 рад (~5.7°-17.2°)
    seed=42  # Фиксированный seed для воспроизводимости
)
aruco_calibrator.image_folder = "./images/aruco"
aruco_calibrator.load_calibration_result("./charuco.npz")
R_cam2gripper, t_cam2gripper = aruco_calibrator.handeye_calibrate(gripper_poses=gripper_positions,
                                                                    pattern="*.jpg", 
                                                                    calib_method="HORAUD")
print("Матрица вращения (камера -> gripper):\n", R_cam2gripper)
print("Вектор перемещения (камера -> gripper):\n", t_cam2gripper)
print()

print("Chessboard handeye калибровка")
gripper_positions = generate_gripper_positions(
    num_positions=10,
    x_limits=(0.05, 0.15),    # X от 5см до 15см
    y_limits=(0.15, 0.25),    # Y от 15см до 25см
    z_limits=(0.25, 0.35),    # Z от 25см до 35см
    roll_limits=(0.0, 0.2),   # Roll от 0 до 0.2 рад (~11.5°)
    pitch_limits=(-0.1, 0.1), # Pitch от -0.1 до 0.1 рад (~±5.7°)
    yaw_limits=(0.1, 0.3),    # Yaw от 0.1 до 0.3 рад (~5.7°-17.2°)
    seed=42  # Фиксированный seed для воспроизводимости
)
chessboard_calibrator.image_folder = "./images/checker"
chessboard_calibrator.load_calibration_result("./charuco.npz")
R_cam2gripper, t_cam2gripper = chessboard_calibrator.handeye_calibrate(gripper_poses=gripper_positions,
                                                                        pattern="*.jpg",)
print("Матрица вращения (камера -> gripper):\n", R_cam2gripper)
print("Вектор перемещения (камера -> gripper):\n", t_cam2gripper)
print()

print("Circle asym handeye калибровка")
gripper_positions = generate_gripper_positions(
    num_positions=10,
    x_limits=(0.05, 0.15),    # X от 5см до 15см
    y_limits=(0.15, 0.25),    # Y от 15см до 25см
    z_limits=(0.25, 0.35),    # Z от 25см до 35см
    roll_limits=(0.0, 0.2),   # Roll от 0 до 0.2 рад (~11.5°)
    pitch_limits=(-0.1, 0.1), # Pitch от -0.1 до 0.1 рад (~±5.7°)
    yaw_limits=(0.1, 0.3),    # Yaw от 0.1 до 0.3 рад (~5.7°-17.2°)
    seed=42  # Фиксированный seed для воспроизводимости
)
circle_asym_calibrator.image_folder = "./images/circle_async"
circle_asym_calibrator.load_calibration_result("./charuco.npz")
R_cam2gripper, t_cam2gripper = circle_asym_calibrator.handeye_calibrate(gripper_poses=gripper_positions,
                                                                        pattern="*.jpg")
print("Матрица вращения (камера -> gripper):\n", R_cam2gripper)
print("Вектор перемещения (камера -> gripper):\n", t_cam2gripper)
print()

print("Circle sym handeye калибровка")
gripper_positions = generate_gripper_positions(
    num_positions=10,
    x_limits=(0.05, 0.15),    # X от 5см до 15см
    y_limits=(0.15, 0.25),    # Y от 15см до 25см
    z_limits=(0.25, 0.35),    # Z от 25см до 35см
    roll_limits=(0.0, 0.2),   # Roll от 0 до 0.2 рад (~11.5°)
    pitch_limits=(-0.1, 0.1), # Pitch от -0.1 до 0.1 рад (~±5.7°)
    yaw_limits=(0.1, 0.3),    # Yaw от 0.1 до 0.3 рад (~5.7°-17.2°)
    seed=42  # Фиксированный seed для воспроизводимости
)
circle_sym_calibrator.image_folder = "./images/circle_sync"
circle_sym_calibrator.load_calibration_result("./charuco.npz")
R_cam2gripper, t_cam2gripper = circle_sym_calibrator.handeye_calibrate(gripper_poses=gripper_positions,
                                                                        pattern="*.jpg")
print("Матрица вращения (камера -> gripper):\n", R_cam2gripper)
print("Вектор перемещения (камера -> gripper):\n", t_cam2gripper)
print()