import cv2
import numpy as np
import matplotlib.pyplot as plt

from cv2 import aruco
from io import BytesIO
from abc import ABC, abstractmethod


class CalibrationBoard(ABC):
    
    PAPER_SIZES = {
        "A4": (210, 297),
        "A3": (297, 420),
        "A5": (148, 210),
        "Letter": (216, 279),
        "Legal": (216, 356)
    }
    
    def __init__(self,
                 squares_x: int,
                 squares_y: int,
                 square_length_mm: float,
                 dpi: int,
                 paper_size: str):
        
        self.squares_x = squares_x
        self.squares_y = squares_y
        self.square_length_mm = square_length_mm
        self.dpi = dpi
        self.paper_size = paper_size

    @property
    def squares_x(self) -> int:
        return self._squares_x
    
    @property
    def squares_y(self) -> int:
        return self._squares_y
    
    @property
    def square_length_mm(self) -> int:
        return self._square_length_mm
    
    @property
    def dpi(self) -> int:
        return self._dpi
    
    @property
    def paper_size(self) -> int:
        return self._paper_size
    
    @squares_x.setter
    def squares_x(self, value: int):
        if not isinstance(value, int) or value < 2:
            raise ValueError("squares_x должен быть целым числом ≥ 2")
        self._squares_x = value
        
    @squares_y.setter
    def squares_y(self, value: int):
        if not isinstance(value, int) or value < 2:
            raise ValueError("squares_y должен быть целым числом ≥ 2")
        self._squares_y = value
        
    @square_length_mm.setter
    def square_length_mm(self, value: float):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("square_length_mm должен быть положительным числом")
        self._square_length_mm = float(value)
        
    @dpi.setter
    def dpi(self, value: int):
        if not isinstance(value, int) or value < 50:
            raise ValueError("dpi должен быть целым числом ≥ 50")
        self._dpi = value
        
    @paper_size.setter
    def paper_size(self, value: str):
        if not isinstance(value, str) or value not in self.PAPER_SIZES:
            raise ValueError(f"paper_size должен быть одним из: {list(self.PAPER_SIZES.keys())}")
        self._paper_size = value
        
    def _compute_canvas_and_scale(self):
        px_per_mm = self.dpi / 25.4
        paper_w_mm, paper_h_mm = self.PAPER_SIZES[self.paper_size]
        canvas_w_px = int(paper_w_mm * px_per_mm)
        canvas_h_px = int(paper_h_mm * px_per_mm)

        board_w_px = int(self.squares_x * self.square_length_mm * px_per_mm)
        board_h_px = int(self.squares_y * self.square_length_mm * px_per_mm)

        # Масштабируем под ширину холста
        scale = canvas_w_px / board_w_px
        scaled_w = canvas_w_px
        scaled_h = int(board_h_px * scale)

        if scaled_h > canvas_h_px:
            # Если высота вышла за пределы — пересчитываем под высоту
            scale = canvas_h_px / board_h_px
            scaled_w = int(board_w_px * scale)
            scaled_h = canvas_h_px

        canvas = 255 * np.ones((canvas_h_px, canvas_w_px), dtype=np.uint8)
        return canvas, scaled_w, scaled_h

    def generate(self) -> np.ndarray:
        canvas, board_w_px, board_h_px = self._compute_canvas_and_scale()
        board_img = self._generate_board_image(board_w_px, board_h_px)

        board_img = cv2.resize(board_img, (board_w_px, board_h_px), interpolation=cv2.INTER_NEAREST)

        offset_x = (canvas.shape[1] - board_img.shape[1]) // 2
        offset_y = (canvas.shape[0] - board_img.shape[0]) // 2

        canvas[offset_y:offset_y + board_h_px, offset_x:offset_x + board_w_px] = board_img
        return canvas

    
    @abstractmethod
    def _generate_board_image(self, 
                              width_px: int, 
                              height_px: int) -> np.ndarray:
        pass


class ArucoBasedBoard(CalibrationBoard):
    ARUCO_DICTS = {
        "4x4_50": aruco.DICT_4X4_50,
        "5x5_100": aruco.DICT_5X5_100,
        "5x5_250": aruco.DICT_5X5_250,
        "6x6_1000": aruco.DICT_6X6_1000,
        "7x7_1000": aruco.DICT_7X7_1000
    }

    def __init__(self,
                 squares_x: int,
                 squares_y: int,
                 square_length_mm: float,
                 dpi: int,
                 paper_size: str,
                 aruco_dict_name: str = "5x5_250"):
        super().__init__(
            squares_x=squares_x,
            squares_y=squares_y,
            square_length_mm=square_length_mm,
            dpi=dpi,
            paper_size=paper_size
        )
        self.aruco_dict_name = aruco_dict_name

    @property
    def aruco_dict_name(self) -> str:
        return self._aruco_dict_name

    @aruco_dict_name.setter
    def aruco_dict_name(self, value: str):
        if value not in self.ARUCO_DICTS:
            raise ValueError(f"aruco_dict_name должен быть одним из: {list(self.ARUCO_DICTS.keys())}")
        self._aruco_dict_name = value

    @classmethod
    def get_aruco_dict(cls) -> dict:
        return cls.ARUCO_DICTS

   
class CharucoBoard(ArucoBasedBoard):
    def __init__(self,
                 squares_x: int,
                 squares_y: int,
                 square_length_mm: float,
                 marker_length_mm: float,
                 dpi: int,
                 paper_size: str,
                 aruco_dict_name: str = "4x4_50"):
        super().__init__(
            squares_x=squares_x,
            squares_y=squares_y,
            square_length_mm=square_length_mm,
            dpi=dpi,
            paper_size=paper_size,
            aruco_dict_name=aruco_dict_name
        )
        self.marker_length_mm = marker_length_mm

    @property
    def marker_length_mm(self) -> float:
        return self._marker_length_mm

    @marker_length_mm.setter
    def marker_length_mm(self, value: float):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("marker_length_mm должен быть положительным числом")
        self._marker_length_mm = float(value)

    def _generate_board_image(self, width_px: int, height_px: int) -> np.ndarray:
        aruco_dict_id = self.ARUCO_DICTS[self.aruco_dict_name]
        aruco_dict = aruco.getPredefinedDictionary(aruco_dict_id)
        board = cv2.aruco.CharucoBoard(
            size=(self.squares_x, self.squares_y),
            squareLength=self.square_length_mm / 1000.0,
            markerLength=self.marker_length_mm / 1000.0,
            dictionary=aruco_dict
        )
        return board.generateImage((width_px, height_px))
    

class ArucoBoard(ArucoBasedBoard):
    def __init__(self,
                 squares_x: int,
                 squares_y: int,
                 square_length_mm: float,
                 marker_length_ratio: float,
                 dpi: int,
                 paper_size: str,
                 aruco_dict_name: str = "5x5_250"):
        super().__init__(
            squares_x=squares_x,
            squares_y=squares_y,
            square_length_mm=square_length_mm,
            dpi=dpi,
            paper_size=paper_size,
            aruco_dict_name=aruco_dict_name
        )
        self.marker_length_ratio = marker_length_ratio

    @property
    def marker_length_ratio(self) -> float:
        return self._marker_length_ratio

    @marker_length_ratio.setter
    def marker_length_ratio(self, value: float):
        if not isinstance(value, (int, float)) or not (0 < value <= 1):
            raise ValueError("marker_length_ratio должен быть числом в диапазоне (0, 1]")
        self._marker_length_ratio = float(value)

    def _generate_board_image(self, width_px: int, height_px: int) -> np.ndarray:
        aruco_dict_id = self.ARUCO_DICTS[self.aruco_dict_name]
        aruco_dict = aruco.getPredefinedDictionary(aruco_dict_id)

        board = aruco.GridBoard(
            size=(self.squares_x, self.squares_y),
            markerLength=self.square_length_mm * self.marker_length_ratio / 1000.0,
            markerSeparation=self.square_length_mm * (1 - self.marker_length_ratio) / 1000.0,
            dictionary=aruco_dict
        )

        return board.generateImage((width_px, height_px))
    

class Checkerboard(CalibrationBoard):
    def _generate_board_image(self, width_px: int, height_px: int) -> np.ndarray:
        base = ((np.indices((self.squares_y, self.squares_x)).sum(axis=0) % 2) * 255).astype(np.uint8)
        board_img = cv2.resize(base, (width_px, height_px), interpolation=cv2.INTER_NEAREST)
        
        return board_img

    

class CircleGridBoard(CalibrationBoard):
    def __init__(self,
                 squares_x: int,
                 squares_y: int,
                 square_length_mm: float,
                 dpi: int,
                 paper_size: str,
                 asymmetric: bool = False):
        super().__init__(squares_x, squares_y, square_length_mm, dpi, paper_size)
        self.asymmetric = asymmetric

    @property
    def asymmetric(self) -> bool:
        return self._asymmetric

    @asymmetric.setter
    def asymmetric(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError("asymmetric должен быть булевым значением")
        self._asymmetric = value

    def _generate_board_image(self, width_px: int, height_px: int) -> np.ndarray:
        board_img = 255 * np.ones((height_px, width_px), dtype=np.uint8)
        
        radius = int(0.25 * min(width_px / self.squares_x, height_px / self.squares_y))
        
        for y in range(self.squares_y):
            for x in range(self.squares_x):
                if self.asymmetric:
                    cx = int((x + 0.5 + 0.5 * (y % 2)) * width_px / self.squares_x)
                else:
                    cx = int((x + 0.5) * width_px / self.squares_x)

                cy = int((y + 0.5) * height_px / self.squares_y)
                
                if 0 <= cx < width_px and 0 <= cy < height_px:
                    cv2.circle(board_img, (cx, cy), radius, 0, -1)

        return board_img


class PDFExporter:
    
    def __call__(self, 
                 canvas: np.ndarray,
                 paper_size: str,
                 dpi: int,
                 paper_sizes: dict):
        
        return self.save(canvas=canvas,
                         paper_size=paper_size,
                         dpi=dpi,
                         paper_sizes=paper_sizes)
    
    @staticmethod
    def save(canvas: np.ndarray,
             paper_size: str,
             dpi: int,
             paper_sizes: dict) -> BytesIO:

        if paper_size not in paper_sizes:
            raise ValueError(f"Неверный формат бумаги: {paper_size}")

        paper_w_mm, paper_h_mm = paper_sizes[paper_size]
        fig_w_inch = paper_w_mm / 25.4
        fig_h_inch = paper_h_mm / 25.4

        fig = plt.figure(figsize=(fig_w_inch, fig_h_inch), dpi=dpi)
        ax = fig.add_axes([0, 0, 1, 1])  # без отступов
        ax.axis('off')

        ax.imshow(canvas, cmap='gray', extent=(0, fig_w_inch, 0, fig_h_inch), aspect='auto')

        buf = BytesIO()
        plt.savefig(buf, format='pdf', dpi=dpi, bbox_inches=None, pad_inches=0)
        plt.close(fig)
        buf.seek(0)

        return buf
    
    
if __name__ == "__main__":
    # Charuco доска
    charuco_board = CharucoBoard(
        squares_x=6,
        squares_y=8,
        square_length_mm=20,
        marker_length_mm=13,
        dpi=300,
        paper_size="A4",
        aruco_dict_name="5x5_250"
    )

    charuco_image = charuco_board.generate()

    charuco_image = charuco_board.generate()
    cv2.imwrite("charuco_debug.png", charuco_image)
    
    # Aruco доска
    aruco_board = ArucoBoard(
        squares_x=3,
        squares_y=5,
        square_length_mm=30,
        marker_length_ratio=0.75,
        dpi=150,
        paper_size="A4",
        aruco_dict_name="4x4_50"
    )

    aruco_image = aruco_board.generate()

    # Экспорт в PDF
    exporter = PDFExporter()
    pdf_bytes = exporter(canvas=charuco_image, paper_size="A4", dpi=150, paper_sizes=charuco_board.PAPER_SIZES)

    with open("charuco_board.pdf", "wb") as f:
        f.write(pdf_bytes.getvalue())
        
    pdf_bytes = exporter(canvas=aruco_image, paper_size="A4", dpi=150, paper_sizes=aruco_board.PAPER_SIZES)
    with open("aruco_board.pdf", "wb") as f:
        f.write(pdf_bytes.getvalue())