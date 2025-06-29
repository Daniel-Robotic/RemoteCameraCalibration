import cv2
import json
import numpy as np
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Tuple, Union, List, Any

from calibration.types import ImageSize, ImagePath, Optional, Dict


class CameraBaseCalibrator(ABC):
    def __init__(
        self,
        image_folder: Union[str, Path],
        pattern_size: Tuple[int, int]
    ) -> None:
        """
        Base abstract class for camera calibration.

        :param image_folder: Path to folder containing calibration images
        :param pattern_size: Pattern size as (columns, rows) of inner corners
        """

        self.image_folder = image_folder
        self.pattern_size = pattern_size
        self._images_size: ImageSize = ()
        self._calibration_result: Optional[Dict[str, Any]] = None

    @property
    def image_folder(self) -> Path:
        return self._image_folder

    @image_folder.setter
    def image_folder(self, value: Union[str, Path]) -> None:
        if isinstance(value, str):
            value = Path(value)

        if not isinstance(value, Path):
            raise TypeError("image_folder must be a string or Path object")

        if not value.exists():
            raise ValueError(f"The specified image folder does not exist: {value}")

        if not value.is_dir():
            raise ValueError(f"The specified path is not a directory: {value}")

        self._image_folder = value

    @property
    def pattern_size(self) -> Tuple[int, int]:
        return self._pattern_size

    @pattern_size.setter
    def pattern_size(self, value: Tuple[int, int]) -> None:
        if not isinstance(value, tuple) or len(value) != 2:
            raise TypeError("pattern_size must be a tuple of two integers")

        if not all(isinstance(val, int) and val >= 2 for val in value):
            raise ValueError("Each dimension in pattern_size must be an integer >= 2")

        self._pattern_size = value

    def _check_images_size(
        self,
        pattern: str = "*"
    ) -> Tuple[ImageSize, List[ImagePath]]:
        """
        Ensures all images in the folder have the same resolution.

        :param pattern: Glob pattern to match image files
        :return: Tuple of reference image size and list of valid image paths
        """
        if not isinstance(pattern, str):
            raise TypeError("pattern must be a string")

        image_sizes: List[ImageSize] = []
        image_paths: List[ImagePath] = list(self._image_folder.glob(pattern))

        if not image_paths:
            raise ValueError("No images found with the given pattern")

        for img_path in image_paths:
            if not img_path.is_file():
                print(f"Skipped non-file path: {img_path}")
                continue

            image = cv2.imread(str(img_path))
            if image is None:
                print(f"Failed to load image: {img_path.name}")
                continue

            height, width = image.shape[:2]
            image_sizes.append((width, height))

        if not image_sizes:
            raise ValueError("No valid images found for calibration")

        ref_size = image_sizes[0]
        for idx, size in enumerate(image_sizes):
            if size != ref_size:
                raise ValueError(
                    f"Image at index {idx} has different resolution: {size} vs {ref_size}"
                )

        return ref_size, image_paths

    def save_calibration_result(self,
                                output_path: Union[str, Path]
                                ):

        """
        Save calibration results to file. Format is determined automatically by file extension.

        Supported formats:
            - .npz: Binary numpy format
            - .json: Human-readable JSON format
            - .txt: Simple text format with matrices

        :param output_path: Path to save the result
        """

        if self._calibration_result is None:
            raise RuntimeError("No calibration data available. Run 'calibrate()' first.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        ext = output_path.suffix.lower()

        if ext == ".npz":
            self._save_npz(output_path)
        elif ext == ".json":
            self._save_json(output_path)
        elif ext == ".txt":
            self._save_txt(output_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}. Use .npz, .json or .txt")

    def _save_npz(self, path: Path) -> None:
        """Save result as compressed .npz file"""
        np.savez_compressed(path, **self._calibration_result)

    def _save_json(self, path: Path) -> None:
        """Save result as JSON file (supports basic types and numpy arrays/dtypes only)"""
        
        def serialize(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.generic):
                return obj.item()
            elif isinstance(obj, dict):
                return {key: serialize(value) for key, value in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [serialize(value) for value in obj]
            else:
                return obj

        serializable_data = serialize(self._calibration_result)

        with open(path, "w") as f:
            json.dump(serializable_data, f, indent=4)

    def _save_txt(self, path: Path) -> None:
        """Save result in human-readable text format"""
        with open(path, "w") as f:
            for key, value in self._calibration_result.items():
                f.write(f"{key.upper()}:\n")
                if isinstance(value, np.ndarray):
                    np.savetxt(f, value, fmt="%.10f")
                else:
                    f.write(f"{value}\n")
                f.write("\n")
    
    @abstractmethod
    def _preprocess_images(self) -> Any:
        """
        Abstract method to preprocess images before corner detection.

        Should be implemented by subclasses.
        """
        pass

    @abstractmethod
    def calibrate(self) -> Any:
        """
        Abstract method to perform camera calibration.

        Should return calibration parameters such as matrix and distortion coefficients.
        """
        pass

    @abstractmethod
    def find_corners(self) -> Any:
        """
        Abstract method to find corner points in images.

        Should return detected corner coordinates.
        """
        pass
