from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db import get_db
from app.config import settings, STORAGE_DIR
from app.models import Task, Page
from app.schemas import (
    TaskCreateResponse, TaskStatusResponse, PagesResponse,
    PageDetail, PipelineResponse, TaskListResponse, TaskListItem,
)
from app.errors import TaskNotFoundError
from app.services.pipeline import pipeline
from app.services.upload_service import create_task_from_uploads

router = APIRouter()


@router.post("/api/tasks", response_model=TaskCreateResponse, status_code=201)
def create_task(
    files: list[UploadFile] = File(...),
    order: str = Form(""),
    db: Session = Depends(get_db),
):
    return create_task_from_uploads(db, files, order, STORAGE_DIR, settings)


@router.get("/api/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundError()
    return TaskStatusResponse(
        task_id=task.id,
        status=task.status,
        page_count=task.page_count,
        error_msg=task.error_msg,
        created_at=task.created_at,
    )


@router.post("/api/tasks/{task_id}/recognize")
def recognize_task(task_id: int, page_no: int = None, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundError()
    result = pipeline.run_recognize(db, task_id, page_no)
    return result


@router.post("/api/tasks/{task_id}/pipeline", response_model=PipelineResponse)
def run_pipeline(task_id: int, db: Session = Depends(get_db)):
    result = pipeline.run_pipeline(db, task_id)
    return PipelineResponse(**result)


@router.get("/api/tasks/{task_id}/pages", response_model=PagesResponse)
def get_pages(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundError()
    pages = db.query(Page).filter(Page.task_id == task_id).order_by(Page.page_no).all()
    return PagesResponse(
        task_id=task_id,
        pages=[
            PageDetail(
                page_no=p.page_no,
                filename=p.filename,
                confidence=p.confidence,
                low_confidence_flag=p.low_confidence_flag,
                failed_flag=p.failed_flag,
                error_msg=p.error_msg,
            )
            for p in pages
        ],
    )


@router.get("/api/tasks", response_model=TaskListResponse)
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.created_at.desc()).all()
    return TaskListResponse(
        tasks=[
            TaskListItem(
                task_id=t.id,
                title=t.title,
                status=t.status,
                page_count=t.page_count,
                created_at=t.created_at,
            )
            for t in tasks
        ]
    )
