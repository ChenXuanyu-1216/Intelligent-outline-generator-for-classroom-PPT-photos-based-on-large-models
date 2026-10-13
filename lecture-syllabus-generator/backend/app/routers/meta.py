from fastapi import APIRouter
from app.config import settings
from app.schemas import HealthResponse, MetaResponse

router = APIRouter()


@router.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        baseline_version=settings.baseline_version,
        model_provider=settings.model_provider,
    )


@router.get("/api/meta", response_model=MetaResponse)
def meta():
    return MetaResponse(
        model_provider=settings.model_provider,
        model_name=settings.model_name,
        allowed_ext=settings.allowed_ext_list,
        max_file_mb=settings.max_file_mb,
        max_files_per_batch=settings.max_files_per_batch,
        recommended_batch=settings.recommended_batch,
        low_confidence_threshold=settings.low_confidence_threshold,
        error_contract={
            "fields": ["code", "message", "retryable"],
            "retryable_true": "前端须显式提供重试按钮",
        },
    )