import pytest
import numpy as np
from io import BytesIO

from calibration import Checkerboard, CircleGridBoard, CharucoBoard, ArucoBoard, PDFExporter


# Тестирование базового класса CalibrationBoard через Checkerboard
def test_calibration_board_init():
    board = Checkerboard(squares_x=7, squares_y=5, square_length_mm=20, dpi=300, paper_size="A4")
    assert board.squares_x == 7
    assert board.squares_y == 5
    assert board.square_length_mm == 20.0
    assert board.dpi == 300
    assert board.paper_size == "A4"


def test_invalid_squares_x():
    with pytest.raises(ValueError):
        Checkerboard(squares_x=1, squares_y=5, square_length_mm=20, dpi=300, paper_size="A4")


def test_invalid_square_length_mm():
    with pytest.raises(ValueError):
        Checkerboard(squares_x=5, squares_y=5, square_length_mm=-10, dpi=300, paper_size="A4")


def test_invalid_dpi():
    with pytest.raises(ValueError):
        Checkerboard(squares_x=5, squares_y=5, square_length_mm=20, dpi=30, paper_size="A4")


def test_invalid_paper_size():
    with pytest.raises(ValueError):
        Checkerboard(squares_x=5, squares_y=5, square_length_mm=20, dpi=300, paper_size="A0")


# Тестирование метода generate у Checkerboard
def test_checkerboard_generate():
    board = Checkerboard(squares_x=8, squares_y=6, square_length_mm=20, dpi=72, paper_size="A4")
    image = board.generate()
    assert isinstance(image, np.ndarray)
    assert len(image.shape) == 2  # grayscale
    assert image.dtype == np.uint8


# Тестирование CharucoBoard
def test_charuco_board_generate():
    charuco = CharucoBoard(
        squares_x=7,
        squares_y=5,
        square_length_mm=20,
        marker_length_mm=15,
        dpi=72,
        paper_size="A4",
        aruco_dict_name="5x5_250"
    )
    image = charuco.generate()
    assert isinstance(image, np.ndarray)
    assert len(image.shape) == 2
    assert image.dtype == np.uint8


def test_invalid_marker_length_mm():
    with pytest.raises(ValueError):
        CharucoBoard(
            squares_x=7,
            squares_y=5,
            square_length_mm=20,
            marker_length_mm=-15,
            dpi=72,
            paper_size="A4"
        )


def test_invalid_aruco_dict_name():
    with pytest.raises(ValueError):
        CharucoBoard(
            squares_x=7,
            squares_y=5,
            square_length_mm=20,
            marker_length_mm=15,
            dpi=72,
            paper_size="A4",
            aruco_dict_name="invalid_dict"
        )


# Тестирование ArucoBoard
def test_aruco_board_generate():
    aruco_board = ArucoBoard(
        squares_x=4,
        squares_y=4,
        square_length_mm=30,
        marker_length_ratio=0.8,
        dpi=72,
        paper_size="A4",
        aruco_dict_name="5x5_250"
    )
    image = aruco_board.generate()
    assert isinstance(image, np.ndarray)
    assert len(image.shape) == 2
    assert image.dtype == np.uint8


def test_invalid_marker_length_ratio():
    with pytest.raises(ValueError):
        ArucoBoard(
            squares_x=4,
            squares_y=4,
            square_length_mm=30,
            marker_length_ratio=-0.1,
            dpi=72,
            paper_size="A4"
        )

    with pytest.raises(ValueError):
        ArucoBoard(
            squares_x=4,
            squares_y=4,
            square_length_mm=30,
            marker_length_ratio=1.5,
            dpi=72,
            paper_size="A4"
        )


def test_invalid_aruco_dict_name_in_aruco_board():
    with pytest.raises(ValueError):
        ArucoBoard(
            squares_x=4,
            squares_y=4,
            square_length_mm=30,
            marker_length_ratio=0.8,
            dpi=72,
            paper_size="A4",
            aruco_dict_name="invalid_dict"
        )


# Тестирование CircleGridBoard
def test_circle_grid_board_generate():
    circle_board = CircleGridBoard(
        squares_x=4,
        squares_y=3,
        square_length_mm=20,
        dpi=72,
        paper_size="A4"
    )
    image = circle_board.generate()
    assert isinstance(image, np.ndarray)
    assert len(image.shape) == 2
    assert image.dtype == np.uint8


def test_circle_grid_asymmetric():
    circle_board = CircleGridBoard(
        squares_x=4,
        squares_y=3,
        square_length_mm=20,
        dpi=72,
        paper_size="A4",
        asymmetric=True
    )
    image = circle_board.generate()
    assert isinstance(image, np.ndarray)


# Тестирование PDFExporter
def test_pdf_exporter():
    board = Checkerboard(squares_x=8, squares_y=6, square_length_mm=20, dpi=72, paper_size="A4")
    canvas = board.generate()

    exporter = PDFExporter()
    pdf_bytes = exporter(canvas=canvas, paper_size="A4", dpi=72, paper_sizes=board.PAPER_SIZES)

    assert isinstance(pdf_bytes, BytesIO)
    assert pdf_bytes.getbuffer().nbytes > 0


def test_pdf_export_invalid_paper_size():
    board = Checkerboard(squares_x=8, squares_y=6, square_length_mm=20, dpi=72, paper_size="A4")
    canvas = board.generate()

    exporter = PDFExporter()
    with pytest.raises(ValueError):
        exporter(canvas=canvas, paper_size="InvalidSize", dpi=72, paper_sizes=board.PAPER_SIZES)