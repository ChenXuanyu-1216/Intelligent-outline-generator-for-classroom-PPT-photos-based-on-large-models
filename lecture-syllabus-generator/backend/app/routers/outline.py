from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Task, Outline
from app.schemas import OutlineResponse, OutlineUpdateRequest, OutlineUpdateResponse, PipelineResponse
from app.errors import TaskNotFoundError, PipelineError
from app.services.pipeline import pipeline

router = APIRouter()


@router.get("/api/tasks/{task_id}/outline", response_model=OutlineResponse)
def get_outline(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundError()
    outline = db.query(Outline).filter(Outline.task_id == task_id).order_by(Outline.version.desc()).first()
    if not outline:
        raise PipelineError("大纲尚未生成，请先执行管道。")
    return OutlineResponse(
        task_id=task_id,
        markdown=outline.markdown,
        version=outline.version,
    )


@router.put("/api/tasks/{task_id}/outline", response_model=OutlineUpdateResponse)
def update_outline(task_id: int, body: OutlineUpdateRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundError()
    latest = db.query(Outline).filter(Outline.task_id == task_id).order_by(Outline.version.desc()).first()
    new_version = (latest.version + 1) if latest else 1
    new_outline = Outline(task_id=task_id, markdown=body.markdown, version=new_version)
    db.add(new_outline)
    db.commit()
    return OutlineUpdateResponse(task_id=task_id, version=new_version)


@router.post("/api/tasks/{task_id}/regenerate", response_model=PipelineResponse)
def regenerate(task_id: int, db: Session = Depends(get_db)):
    result = pipeline.run_pipeline(db, task_id)
    return PipelineResponse(**result)