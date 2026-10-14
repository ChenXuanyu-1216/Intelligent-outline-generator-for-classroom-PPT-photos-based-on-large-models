from sqlalchemy.orm import Session
from app.models import Task, Page, KnowledgePoint, Outline, OutlineNode
from app.services.recognizer import get_recognizer, RecognitionResult
from app.services.extractor import Extractor
from app.services.clusterer import Clusterer
from app.services.outline_service import outline_service
from app.errors import AppError, PipelineError, TaskNotFoundError


class Pipeline:
    def __init__(self):
        self.recognizer = get_recognizer()
        self.extractor = Extractor()
        self.clusterer = Clusterer()

    def run_recognize(self, db: Session, task_id: int, page_no: int | None = None) -> dict:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise TaskNotFoundError()

        pages = db.query(Page).filter(Page.task_id == task_id).order_by(Page.page_no).all()
        selected_pages = pages
        if page_no is not None:
            selected_pages = [p for p in pages if p.page_no == page_no]
        if not selected_pages:
            raise AppError("PAGE_NOT_FOUND", "页面不存在。", status_code=404)

        task.status = "running"
        task.error_msg = None
        db.commit()
        for page in selected_pages:
            self._recognize_page(page)

        if all(p.failed_flag for p in pages):
            task.status = "failed"
            task.error_msg = "所有页面识别失败，请重试。"
        elif any(p.failed_flag for p in pages):
            task.status = "partial"
        elif any(p.recognized_text is None for p in pages):
            task.status = "pending"
        else:
            task.status = "success"
        db.commit()

        return {"task_id": task_id, "status": task.status}

    def run_pipeline(self, db: Session, task_id: int) -> dict:
        try:
            return self._run_pipeline(db, task_id)
        except Exception as exc:
            db.rollback()
            task = db.get(Task, task_id)
            if task is not None:
                task.status = "failed"
                task.error_msg = exc.message if isinstance(exc, AppError) else "大纲生成失败，请重试。"
                db.commit()
            raise

    def _recognize_page(self, page: Page) -> bool:
        try:
            result = self.recognizer.recognize(page.page_no, page.file_path)
            page.recognized_text = result.text
            page.recognized_structured = result.structured
            page.confidence = result.confidence
            page.low_confidence_flag = result.low_confidence
            page.failed_flag = False
            page.error_msg = None
            return True
        except Exception as exc:
            # Failed retries cannot reuse stale successful recognition.
            page.recognized_text = None
            page.recognized_structured = None
            page.confidence = 0.0
            page.low_confidence_flag = False
            page.failed_flag = True
            page.error_msg = exc.message if isinstance(exc, AppError) else "页面识别失败，请重试。"
            return False

    def _run_pipeline(self, db: Session, task_id: int) -> dict:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise TaskNotFoundError()

        task.status = "running"
        task.error_msg = None
        db.commit()

        pages = db.query(Page).filter(Page.task_id == task_id).order_by(Page.page_no).all()
        if not pages:
            raise PipelineError("没有页面数据。")

        all_points = []
        page_titles = {}
        any_failed = False

        for page in pages:
            if page.failed_flag:
                any_failed = True
                continue

            if not page.recognized_text:
                if not self._recognize_page(page):
                    any_failed = True
                    continue
            structured = page.recognized_structured
            # Text-only providers return a placeholder title and no points.
            # Reconstruct their real title from text instead of using that shell.
            if not structured or not structured.get("points"):
                structured = self._reconstruct_structured(page.recognized_text, page.page_no)
            recognition = RecognitionResult(
                text=page.recognized_text,
                confidence=page.confidence,
                low_confidence=page.low_confidence_flag,
                structured=structured,
            )

            title = recognition.structured.get("title", f"页面{page.page_no}")
            page_titles[page.page_no] = title

            extracted = self.extractor.extract(page.id, page.page_no, recognition)
            all_points.extend(extracted)

        db.commit()

        deduped = self.extractor.dedup_cross_page(all_points)
        if not deduped:
            raise PipelineError("没有可用于生成大纲的识别内容，请重试失败页面。")

        db.query(KnowledgePoint).filter(KnowledgePoint.task_id == task_id).delete()

        for kp in deduped:
            db.add(KnowledgePoint(
                task_id=task_id,
                page_id=kp.page_id,
                content=kp.content,
                kp_type=kp.kp_type,
                source_type=kp.source_type,
                source_pages=kp.source_pages,
                dedup_key=kp.dedup_key,
            ))
        db.flush()

        modules = self.clusterer.cluster(deduped, page_titles)
        markdown = outline_service.render_markdown(modules)

        db.query(OutlineNode).filter(
            OutlineNode.outline_id.in_(
                db.query(Outline.id).filter(Outline.task_id == task_id)
            )
        ).delete(synchronize_session=False)
        db.query(Outline).filter(Outline.task_id == task_id).delete()
        db.flush()

        outline = Outline(task_id=task_id, markdown=markdown, version=1)
        db.add(outline)
        db.flush()

        for mi, module in enumerate(modules):
            node = OutlineNode(
                outline_id=outline.id,
                level=1,
                title=module.title,
                source_pages=module.source_pages,
                sort_order=mi,
            )
            db.add(node)
            db.flush()
            for ki, kp in enumerate(module.knowledge_points):
                db.add(OutlineNode(
                    outline_id=outline.id,
                    level=2,
                    title=kp.content,
                    content=kp.content,
                    source_type=kp.source_type,
                    source_pages=kp.source_pages,
                    parent_id=node.id,
                    sort_order=ki,
                ))
        if any_failed:
            task.status = "partial"
        else:
            task.status = "success"
        db.commit()

        return {
            "task_id": task_id,
            "status": task.status,
            "knowledge_point_count": len(deduped),
            "module_count": len(modules),
        }

    def _reconstruct_structured(self, text: str, page_no: int) -> dict:
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        if not lines:
            return {"title": f"页面{page_no}", "points": []}
        title = lines[0].lstrip("# ").strip()
        points = []
        for line in lines[1:]:
            content = line.lstrip("- ").strip()
            if content:
                points.append({"content": content, "kp_type": "concept", "source_type": "来源待核对"})
        return {"title": title, "points": points}


pipeline = Pipeline()
