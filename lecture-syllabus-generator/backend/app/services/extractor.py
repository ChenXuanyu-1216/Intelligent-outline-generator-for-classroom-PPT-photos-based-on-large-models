from dataclasses import dataclass
from app.services.recognizer import RecognitionResult


@dataclass
class ExtractedKnowledgePoint:
    content: str
    kp_type: str
    source_type: str
    source_pages: str
    page_id: int
    dedup_key: str


class Extractor:
    def extract(self, page_id: int, page_no: int, recognition: RecognitionResult) -> list[ExtractedKnowledgePoint]:
        source_tag = f"P{page_no}"
        points = recognition.structured.get("points", [])

        if not points and recognition.text:
            lines = [l.strip().lstrip("- ").strip() for l in recognition.text.strip().split("\n") if l.strip()]
            if lines:
                title = lines[0]
                points = [{"content": l, "kp_type": "concept", "source_type": "课堂原话"} for l in lines[1:]]
                if not points:
                    points = [{"content": title, "kp_type": "concept", "source_type": "课堂原话"}]

        result = []
        for p in points:
            content = p.get("content", "").strip()
            if not content:
                continue
            kp_type = p.get("kp_type", "concept")
            source_type = p.get("source_type", "课堂原话")
            dedup_key = content.lower().replace(" ", "").replace("：", ":")
            result.append(ExtractedKnowledgePoint(
                content=content,
                kp_type=kp_type,
                source_type=source_type,
                source_pages=source_tag,
                page_id=page_id,
                dedup_key=dedup_key,
            ))
        return result

    def dedup_cross_page(self, all_points: list[ExtractedKnowledgePoint]) -> list[ExtractedKnowledgePoint]:
        merged: dict[str, ExtractedKnowledgePoint] = {}
        for kp in all_points:
            if kp.dedup_key in merged:
                existing = merged[kp.dedup_key]
                existing_pages = set(existing.source_pages.split(","))
                new_pages = set(kp.source_pages.split(","))
                combined = ",".join(sorted(existing_pages | new_pages, key=lambda x: int(x[1:])))
                merged[kp.dedup_key] = ExtractedKnowledgePoint(
                    content=existing.content,
                    kp_type=existing.kp_type,
                    source_type=existing.source_type,
                    source_pages=combined,
                    page_id=existing.page_id,
                    dedup_key=existing.dedup_key,
                )
            else:
                merged[kp.dedup_key] = kp
        return list(merged.values())