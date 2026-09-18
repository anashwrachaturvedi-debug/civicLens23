"""
app/api/v1/ai.py

CivicLens AI Backend - AI Detection API Router
------------------------------------------------
Handles image-based civic issue detection (e.g., potholes, garbage, damaged
infrastructure) using a YOLOv8 model. Accepts uploaded images, runs inference
via the AI service layer, optionally persists the annotated image to
Cloudinary, and stores detection metadata in the database.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import (
    DetectionHistoryResponse,
    DetectionResponse,
    DetectionResultSchema,
)
from app.services.ai_service import AIDetectionService
from app.services.cloudinary_service import CloudinaryService
from app.utils.file_validators import validate_image_file

router = APIRouter(
    prefix="/ai",
    tags=["AI Detection"],
)


def get_ai_service() -> AIDetectionService:
    """Dependency provider for the YOLOv8 detection service (singleton-style)."""
    return AIDetectionService(
        model_path=settings.YOLO_MODEL_PATH,
        confidence_threshold=settings.YOLO_CONFIDENCE_THRESHOLD,
        iou_threshold=settings.YOLO_IOU_THRESHOLD,
    )


def get_cloudinary_service() -> CloudinaryService:
    """Dependency provider for the Cloudinary upload service."""
    return CloudinaryService()


# ------------------------------------------------------------------------------
# POST /api/v1/ai/detect
# ------------------------------------------------------------------------------
@router.post(
    "/detect",
    response_model=DetectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run AI detection on an uploaded image",
    description=(
        "Uploads an image, runs YOLOv8 object detection to identify civic "
        "issues (e.g., potholes, garbage dumps, damaged public property), "
        "uploads the annotated result to Cloudinary, and persists the "
        "detection record."
    ),
)
async def detect_civic_issue(
    file: UploadFile = File(..., description="Image file to analyze"),
    latitude: Optional[float] = Query(None, description="Capture location latitude"),
    longitude: Optional[float] = Query(None, description="Capture location longitude"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ai_service: AIDetectionService = Depends(get_ai_service),
    cloudinary_service: CloudinaryService = Depends(get_cloudinary_service),
) -> DetectionResponse:
    """
    Run object detection on an uploaded image and store the results.
    """
    validate_image_file(
        file,
        allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS,
        max_size_mb=settings.MAX_UPLOAD_SIZE_MB,
    )

    try:
        image_bytes = await file.read()
        logger.info(
            "AI detection requested | user_id={} | filename={} | size={} bytes",
            current_user.id,
            file.filename,
            len(image_bytes),
        )

        # Run YOLOv8 inference (CPU-bound; offloaded to thread pool internally)
        detection_result: DetectionResultSchema = await ai_service.run_inference(
            image_bytes=image_bytes,
            original_filename=file.filename,
        )

        # Upload original + annotated image to Cloudinary
        upload_result = await cloudinary_service.upload_image(
            image_bytes=detection_result.annotated_image_bytes,
            folder="civiclens/detections",
            public_id_prefix=f"user_{current_user.id}",
        )

        # Persist detection record to the database
        detection_record = await ai_service.save_detection_record(
            db=db,
            user_id=current_user.id,
            image_url=upload_result.secure_url,
            detections=detection_result.detections,
            confidence_scores=detection_result.confidence_scores,
            latitude=latitude,
            longitude=longitude,
        )

        logger.success(
            "Detection completed | detection_id={} | objects_found={}",
            detection_record.id,
            len(detection_result.detections),
        )

        return DetectionResponse(
            id=detection_record.id,
            image_url=upload_result.secure_url,
            detections=detection_result.detections,
            confidence_scores=detection_result.confidence_scores,
            created_at=detection_record.created_at,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("AI detection failed | user_id={} | error={}", current_user.id, str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI detection failed. Please try again later.",
        ) from exc


# ------------------------------------------------------------------------------
# GET /api/v1/ai/history
# ------------------------------------------------------------------------------
@router.get(
    "/history",
    response_model=List[DetectionHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get detection history for the current user",
)
async def get_detection_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ai_service: AIDetectionService = Depends(get_ai_service),
) -> List[DetectionHistoryResponse]:
    """
    Retrieve paginated AI detection history for the authenticated user.
    """
    try:
        records = await ai_service.get_user_detections(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
        return records
    except Exception as exc:
        logger.exception("Failed to fetch detection history | user_id={}", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve detection history.",
        ) from exc


# ------------------------------------------------------------------------------
# GET /api/v1/ai/detections/{detection_id}
# ------------------------------------------------------------------------------
@router.get(
    "/detections/{detection_id}",
    response_model=DetectionHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single detection record by ID",
)
async def get_detection_by_id(
    detection_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ai_service: AIDetectionService = Depends(get_ai_service),
) -> DetectionHistoryResponse:
    """
    Fetch a specific detection record, ensuring it belongs to the requester.
    """
    record = await ai_service.get_detection_by_id(
        db=db, detection_id=detection_id, user_id=current_user.id
    )
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection record not found.",
        )
    return record


# ------------------------------------------------------------------------------
# DELETE /api/v1/ai/detections/{detection_id}
# ------------------------------------------------------------------------------
@router.delete(
    "/detections/{detection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a detection record",
)
async def delete_detection(
    detection_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ai_service: AIDetectionService = Depends(get_ai_service),
    cloudinary_service: CloudinaryService = Depends(get_cloudinary_service),
) -> None:
    """
    Delete a detection record and its associated Cloudinary asset.
    """
    record = await ai_service.get_detection_by_id(
        db=db, detection_id=detection_id, user_id=current_user.id
    )
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection record not found.",
        )

    try:
        await cloudinary_service.delete_image(image_url=record.image_url)
        await ai_service.delete_detection_record(db=db, detection_id=detection_id)
        logger.info("Detection deleted | detection_id={} | user_id={}", detection_id, current_user.id)
    except Exception as exc:
        logger.exception("Failed to delete detection | detection_id={}", detection_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete detection record.",
        ) from exc