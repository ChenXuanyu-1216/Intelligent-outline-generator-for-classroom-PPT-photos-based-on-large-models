import os
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db import get_db
from app.config import settings, STORAGE_DIR
from app.models import Task, Page
from app.schemas import (
    TaskCreateResponse, TaskStatusResponse, PagesResponse,
    PageDetail, PipelineResponse, TaskListResponse, TaskListItem,
)
from app.errors import FileFormatError, FileTooLargeError, TooManyFilesError, TaskNotFoundError
from app.services.pipeline import pipeline

router = APIRouter()


@router.post("/api/tasks", response_model=TaskCreateResponse, status_code=201)
def create_task(
    files: list[UploadFile] = File(...),
    order: str = Form(""),
    db: Session = Depends(get_db),
):
    if len(files) > settings.max_files_per_batch:
        raise TooManyFilesError()

    rejected = []
    valid_files = []
    for i, f in enumerate(files):
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in settings.allowed_ext_list:
            rejected.append({"filename": f.filename, "reason": f"格式不支持：{ext}"})
            continue
        valid_files.append((i, f))

    if not valid_files:
        raise FileFormatError("所有文件格式均不支持。")

    if order.strip():
        order_list = [int(x.strip()) for x in order.split(",") if x.strip()]
    else:
        order_list = list(range(1, len(valid_files) + 1))

    sorted_files = []
    for pos, original_idx in enumerate(order_list):
        matching = [(i, f) for i, f in valid_files if i == original_idx - 1]
        if matching:
            sorted_files.append((pos + 1, matching[0][1]))

    if not sorted_files:
        sorted_files = [(pos + 1, f) for pos, (_, f) in enumerate(valid_files)]

    task = Task(title="未命名任务", status="pending", page_count=len(sorted_files))
    db.add(task)
    db.commit()
    db.refresh(task)

    task_dir = STORAGE_DIR / str(task.id)
    task_dir.mkdir(parents=True, exist_ok=True)

    for page_no, f in sorted_files:
        ext = os.path.splitext(f.filename)[1].lower()
        saved_name = f"page_{page_no}{ext}"
        saved_path = task_dir / saved_name
        content = f.file.read()
        if len(content) > settings.max_file_mb * 1024 * 1024:
            rejected.append({"filename": f.filename, "reason": "文件大小超过限制"})
            continue
        with open(saved_path, "wb") as out:
            out.write(content)
        db.add(Page(
            task_id=task.id,
            page_no=page_no,
            filename=f.filename,
            file_path=str(saved_path),
            confidence=0.0,
            low_confidence_flag=False,
            failed_flag=False,
        ))

    db.commit()
    db.refresh(task)

    return TaskCreateResponse(
        task_id=task.id,
        page_count=task.page_count,
        rejected=rejected,
    )


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