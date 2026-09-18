"""
app/services/ai_service.py

AI inference service for detecting infrastructure/civic issues (e.g. potholes,
garbage, damaged signage, etc.) from uploaded images using YOLOv8.

This module is responsible ONLY for:
    - Loading and holding a singleton YOLOv8 model instance
    - Preprocessing uploaded image bytes into a model-ready format
    - Running inference (in a thread, to keep the event loop free)
    - Structuring and returning detection results

It intentionally contains NO API route or database logic.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import cv2
import numpy as np

try:
    from ultralytics import YOLO
except ImportError as exc:  # pragma: no cover - environment guard
    raise ImportError(
        "The 'ultralytics' package is required for AIService. "
        "Install it with: pip install ultralytics"
    ) from exc


logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #

class AIServiceError(Exception):
    """Base exception for all AI service related errors."""


class ModelLoadError(AIServiceError):
    """Raised when the YOLOv8 model fails to load."""


class InvalidImageError(AIServiceError):
    """Raised when the provided image bytes cannot be decoded or are invalid."""


class InferenceError(AIServiceError):
    """Raised when the model fails during inference."""


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class BoundingBox:
    """Pixel-space bounding box coordinates (top-left, bottom-right)."""

    x1: float
    y1: float
    x2: float
    y2: float

    def to_dict(self) -> dict[str, float]:
        """Serialize bounding box to a plain dict."""
        return {"x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2}


@dataclass(frozen=True)
class Detection:
    """A single detected object/issue within an image."""

    label: str
    category: str
    confidence: float
    bounding_box: BoundingBox

    def to_dict(self) -> dict[str, Any]:
        """Serialize detection to a plain dict, suitable for JSON responses."""
        return {
            "label": self.label,
            "category": self.category,
            "confidence": round(self.confidence, 4),
            "bounding_box": self.bounding_box.to_dict(),
        }


@dataclass
class InferenceResult:
    """Aggregated result of running inference on a single image."""

    detections: list[Detection] = field(default_factory=list)
    image_width: int = 0
    image_height: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize the full inference result to a plain dict."""
        return {
            "image_width": self.image_width,
            "image_height": self.image_height,
            "detection_count": len(self.detections),
            "detections": [d.to_dict() for d in self.detections],
        }


# --------------------------------------------------------------------------- #
# Category mapping
# --------------------------------------------------------------------------- #

# Maps raw YOLO class labels -> higher-level "issue" categories used by the
# application layer. Unmapped labels fall back to "uncategorized".
DEFAULT_ISSUE_CATEGORY_MAP: Final[dict[str, str]] = {
    "pothole": "road_damage",
    "crack": "road_damage",
    "garbage": "sanitation",
    "trash": "sanitation",
    "graffiti": "vandalism",
    "broken_sign": "infrastructure",
    "streetlight": "infrastructure",
}

UNCATEGORIZED_LABEL: Final[str] = "uncategorized"


# --------------------------------------------------------------------------- #
# AI Service (singleton)
# --------------------------------------------------------------------------- #

class AIService:
    """
    Singleton service that owns the YOLOv8 model lifecycle and exposes
    async-friendly methods for preprocessing images and running inference.

    Usage:
        service = AIService.get_instance(model_path="models/best.pt")
        result = await service.detect_issues(image_bytes)
    """

    _instance: "AIService | None" = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(
        self,
        model_path: str | Path,
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        category_map: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize the AIService. Prefer using `get_instance()` instead of
        calling this constructor directly, to preserve the singleton pattern.

        Args:
            model_path: Filesystem path to the YOLOv8 weights (.pt file).
            confidence_threshold: Minimum confidence score to keep a detection.
            iou_threshold: IoU threshold used for NMS during inference.
            category_map: Optional mapping of raw label -> issue category.

        Raises:
            ModelLoadError: If the model cannot be loaded from `model_path`.
        """
        self._model_path = Path(model_path)
        self._confidence_threshold = confidence_threshold
        self._iou_threshold = iou_threshold
        self._category_map = category_map or DEFAULT_ISSUE_CATEGORY_MAP
        self._model: YOLO | None = None

        self._load_model()

    # ------------------------------------------------------------------- #
    # Singleton access
    # ------------------------------------------------------------------- #

    @classmethod
    async def get_instance(
        cls,
        model_path: str | Path = "models/yolov8n.pt",
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        category_map: dict[str, str] | None = None,
    ) -> "AIService":
        """
        Retrieve the singleton AIService instance, creating and loading the
        model on first call. Safe for concurrent async callers.

        Args:
            model_path: Filesystem path to the YOLOv8 weights (.pt file).
                        Only used on first initialization.
            confidence_threshold: Minimum confidence score to keep a detection.
            iou_threshold: IoU threshold used for NMS during inference.
            category_map: Optional mapping of raw label -> issue category.

        Returns:
            The singleton AIService instance.

        Raises:
            ModelLoadError: If the model fails to load on first initialization.
        """
        if cls._instance is not None:
            return cls._instance

        async with cls._lock:
            # Re-check inside the lock in case another coroutine won the race.
            if cls._instance is None:
                logger.info("Initializing AIService singleton (model=%s)", model_path)
                loop = asyncio.get_running_loop()
                instance = await loop.run_in_executor(
                    None,
                    lambda: cls(
                        model_path=model_path,
                        confidence_threshold=confidence_threshold,
                        iou_threshold=iou_threshold,
                        category_map=category_map,
                    ),
                )
                cls._instance = instance
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Clear the cached singleton instance (primarily useful for testing)."""
        cls._instance = None

    # ------------------------------------------------------------------- #
    # Model lifecycle
    # ------------------------------------------------------------------- #

    def _load_model(self) -> None:
        """
        Load the YOLOv8 model from disk into memory.

        Raises:
            ModelLoadError: If the weights file is missing or fails to load.
        """
        if not self._model_path.exists():
            logger.error("Model weights not found at path: %s", self._model_path)
            raise ModelLoadError(f"Model weights not found at: {self._model_path}")

        try:
            logger.info("Loading YOLOv8 model from %s", self._model_path)
            self._model = YOLO(str(self._model_path))
            logger.info("YOLOv8 model loaded successfully.")
        except Exception as exc:  # noqa: BLE001 - wrap all loader failures
            logger.exception("Failed to load YOLOv8 model from %s", self._model_path)
            raise ModelLoadError(
                f"Failed to load YOLOv8 model from '{self._model_path}': {exc}"
            ) from exc

    @property
    def is_ready(self) -> bool:
        """Whether the underlying model has been successfully loaded."""
        return self._model is not None

    # ------------------------------------------------------------------- #
    # Preprocessing
    # ------------------------------------------------------------------- #

    @staticmethod
    def _decode_image(image_bytes: bytes) -> np.ndarray:
        """
        Decode raw image bytes into a BGR NumPy array using OpenCV.

        Args:
            image_bytes: Raw bytes of the uploaded image file.

        Returns:
            A NumPy array representing the decoded image (H, W, 3) in BGR.

        Raises:
            InvalidImageError: If the bytes are empty or cannot be decoded.
        """
        if not image_bytes:
            raise InvalidImageError("Received empty image payload.")

        np_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)

        if image is None:
            raise InvalidImageError(
                "Could not decode image bytes. File may be corrupted or "
                "not a supported image format."
            )
        return image

    @staticmethod
    def _validate_image_shape(image: np.ndarray) -> None:
        """
        Ensure decoded image has a valid, non-degenerate shape.

        Args:
            image: Decoded BGR image array.

        Raises:
            InvalidImageError: If the image has zero width/height or is
                                otherwise malformed.
        """
        if image.ndim != 3 or image.shape[2] != 3:
            raise InvalidImageError(f"Unexpected image shape: {image.shape}")

        height, width = image.shape[:2]
        if height == 0 or width == 0:
            raise InvalidImageError("Decoded image has zero width or height.")

    def _preprocess(self, image_bytes: bytes) -> np.ndarray:
        """
        Full preprocessing pipeline: decode + validate.

        YOLOv8's own predict() call handles resizing/normalization internally,
        so this stage focuses on producing a clean, valid BGR array for it.

        Args:
            image_bytes: Raw bytes of the uploaded image file.

        Returns:
            Validated BGR NumPy image array ready for inference.

        Raises:
            InvalidImageError: If decoding or validation fails.
        """
        image = self._decode_image(image_bytes)
        self._validate_image_shape(image)
        return image

    async def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """
        Async wrapper around the synchronous preprocessing pipeline.

        Args:
            image_bytes: Raw bytes of the uploaded image file.

        Returns:
            Validated BGR NumPy image array ready for inference.

        Raises:
            InvalidImageError: If decoding or validation fails.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._preprocess, image_bytes)

    # ------------------------------------------------------------------- #
    # Inference
    # ------------------------------------------------------------------- #

    def _map_category(self, label: str) -> str:
        """
        Map a raw YOLO class label to a higher-level issue category.

        Args:
            label: Raw class label as reported by the model.

        Returns:
            The mapped category, or "uncategorized" if no mapping exists.
        """
        return self._category_map.get(label.lower(), UNCATEGORIZED_LABEL)

    def _run_inference_sync(self, image: np.ndarray) -> InferenceResult:
        """
        Synchronously run YOLOv8 inference on a decoded image array.

        Args:
            image: Validated BGR NumPy image array.

        Returns:
            An InferenceResult containing structured detections.

        Raises:
            InferenceError: If the model is not loaded or inference fails.
        """
        if self._model is None:
            raise InferenceError("Model is not loaded; cannot run inference.")

        height, width = image.shape[:2]

        try:
            results = self._model.predict(
                source=image,
                conf=self._confidence_threshold,
                iou=self._iou_threshold,
                verbose=False,
            )
        except Exception as exc:  # noqa: BLE001 - wrap all inference failures
            logger.exception("YOLOv8 inference failed.")
            raise InferenceError(f"Inference failed: {exc}") from exc

        detections: list[Detection] = []

        for result in results:
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue

            names = result.names or {}

            for box in boxes:
                try:
                    cls_id = int(box.cls.item())
                    confidence = float(box.conf.item())
                    x1, y1, x2, y2 = (float(v) for v in box.xyxy[0].tolist())
                except (AttributeError, ValueError, IndexError) as exc:
                    logger.warning("Skipping malformed detection box: %s", exc)
                    continue

                label = names.get(cls_id, f"class_{cls_id}")
                category = self._map_category(label)

                detections.append(
                    Detection(
                        label=label,
                        category=category,
                        confidence=confidence,
                        bounding_box=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
                    )
                )

        logger.info("Inference complete: %d detection(s) found.", len(detections))

        return InferenceResult(
            detections=detections,
            image_width=width,
            image_height=height,
        )

    async def run_inference(self, image: np.ndarray) -> InferenceResult:
        """
        Async wrapper around synchronous YOLOv8 inference, executed in a
        worker thread so the event loop is not blocked.

        Args:
            image: Validated BGR NumPy image array.

        Returns:
            An InferenceResult containing structured detections.

        Raises:
            InferenceError: If inference fails.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._run_inference_sync, image)

    # ------------------------------------------------------------------- #
    # Public high-level API
    # ------------------------------------------------------------------- #

    async def detect_issues(self, image_bytes: bytes) -> dict[str, Any]:
        """
        High-level entry point: preprocess raw image bytes, run inference,
        and return a JSON-serializable dict of results.

        Args:
            image_bytes: Raw bytes of the uploaded image file.

        Returns:
            A dict containing image dimensions and a list of detections,
            each with label, issue category, confidence score, and
            bounding box coordinates.

        Raises:
            InvalidImageError: If the image bytes are invalid or undecodable.
            InferenceError: If the model fails during inference.
            AIServiceError: For any other unexpected service-level failure.
        """
        try:
            image = await self.preprocess_image(image_bytes)
            result = await self.run_inference(image)
            return result.to_dict()
        except (InvalidImageError, InferenceError):
            # Already well-formed, specific errors — re-raise as-is for the
            # calling layer (e.g. API route) to translate into HTTP responses.
            raise
        except Exception as exc:  # noqa: BLE001 - final safety net
            logger.exception("Unexpected error during detect_issues().")
            raise AIServiceError(f"Unexpected error during detection: {exc}") from exc