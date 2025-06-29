from calibration import (ChessboardCalibrator, 
                        CircleGridCalibrator, 
                        ArucoBoardCalibrator,
                        CharucoBoardCalibrator)


checker_folder = "/home/daniel/dev/docker_dev/web_service/calibration_module/images/checker"
circle_async_folder = "/home/daniel/dev/docker_dev/web_service/calibration_module/images/circle_async"
circle_sync_folder = "/home/daniel/dev/docker_dev/web_service/calibration_module/images/circle_sync"
aruco_folder = "/home/daniel/dev/docker_dev/web_service/calibration_module/images/aruco"
charuco_folder = "/home/daniel/dev/docker_dev/web_service/calibration_module/images/charuco"


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
    
circle_sym_calibrator = CircleGridCalibrator(image_folder=circle_async_folder,
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
                                           aruco_dict_name="5x5_250",
                                           pattern_length_mm=square_length_mm,
                                           marker_length_mm=marker_length_mm)


print("Chessboard калибровка")
try:
    chessboard_result = chessboard_calibrator.calibrate()
    chessboard_calibrator.save_calibration_result(output_path="./chessboard.npz")
    print("Точность калибровки:", chessboard_result["ret"])
    print("Матрица камеры:", chessboard_result["matrix"].tolist())
    print("Дисторсия:", chessboard_result["distortion"])
except Exception as e:
    print(e)
print()

print("Circle asym калибровка")
try:
    circle_async_result = circle_asym_calibrator.calibrate()
    print("Точность калибровки:", circle_async_result["ret"])
    print("Матрица камеры:", circle_async_result["matrix"].tolist())
    print("Дисторсия:", circle_async_result["distortion"])
except Exception as e:
    print(e)
print()

print("Circle sym калибровка")
try:
    circle_sync_result = circle_sym_calibrator.calibrate()
    print("Точность калибровки:", circle_sync_result["ret"])
    print("Матрица камеры:", circle_sync_result["matrix"].tolist())
    print("Дисторсия:", circle_sync_result["distortion"])
except Exception as e:
    print(e)
print()

print("Aruco калибровка")
try:
    aruco_result = aruco_calibrator.calibrate()
    aruco_calibrator.save_calibration_result(output_path="./aruco.txt")
    print("Точность калибровки:", aruco_result["ret"])
    print("Матрица камеры:", aruco_result["matrix"].tolist())
    print("Дисторсия:", aruco_result["distortion"])
except Exception as e:
    print(e)
print()

print("Charuco калибровка")
# try:
charuco_result = charuco_calibrator.calibrate()
charuco_calibrator.save_calibration_result(output_path="./charuco.json")
print("Точность калибровки:", charuco_result["ret"])
print("Матрица камеры:", charuco_result["matrix"].tolist())
print("Дисторсия:", charuco_result["distortion"])
# except Exception as e:
    # print(e)
# print()

