from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
import httpx
from app.config import settings
from app.errors import ModelTimeoutError, RecognitionFailedError


@dataclass
class RecognitionPoint:
    content: str
    kp_type: str = "concept"
    source_type: str = "课堂原话"


@dataclass
class RecognitionResult:
    text: str
    confidence: float = 0.95
    low_confidence: bool = False
    structured: dict = field(default_factory=dict)


_MOCK_PAGES = {
    1: {
        "title": "数据库设计概述",
        "points": [
            RecognitionPoint("关系数据库基本概念", "concept", "课堂原话"),
            RecognitionPoint("数据模型的三要素：数据结构、数据操作、数据约束", "concept", "AI推断"),
            RecognitionPoint("ER图是概念模型设计的核心工具", "method", "课堂原话"),
            RecognitionPoint("数据库设计的目标是减少冗余、保持一致性", "conclusion", "AI推断"),
        ],
    },
    2: {
        "title": "范式与函数依赖",
        "points": [
            RecognitionPoint("第一范式要求属性不可再分", "concept", "课堂原话"),
            RecognitionPoint("第二范式消除部分函数依赖", "concept", "课堂原话"),
            RecognitionPoint("第三范式消除传递函数依赖", "concept", "AI推断"),
            RecognitionPoint("BCNF是第三范式的加强形式", "conclusion", "AI推断"),
        ],
    },
    3: {
        "title": "索引与查询优化",
        "points": [
            RecognitionPoint("B+树是数据库最常用的索引结构", "concept", "课堂原话"),
            RecognitionPoint("索引选择需要权衡查询性能与写入开销", "method", "AI推断"),
            RecognitionPoint("覆盖索引可以避免回表查询", "conclusion", "课堂原话"),
            RecognitionPoint("查询优化器基于代价选择执行计划", "concept", "AI推断"),
        ],
    },
}


class Recognizer(ABC):
    @abstractmethod
    def recognize(self, page_no: int, file_path: str) -> RecognitionResult:
        pass


class MockRecognizer(Recognizer):
    def recognize(self, page_no: int, file_path: str) -> RecognitionResult:
        page_data = _MOCK_PAGES.get(page_no)
        if page_data is None:
            generic = _MOCK_PAGES[((page_no - 1) % 3) + 1]
            title = f"模块{page_no}"
            points = [
                RecognitionPoint(
                    f"知识点{page_no}-{i+1}",
                    p.kp_type,
                    p.source_type,
                )
                for i, p in enumerate(generic["points"])
            ]
            page_data = {"title": title, "points": points}

        text_lines = [page_data["title"]]
        for p in page_data["points"]:
            text_lines.append(f"  - {p.content}")
        text = "\n".join(text_lines)

        return RecognitionResult(
            text=text,
            confidence=0.95,
            low_confidence=False,
            structured={
                "title": page_data["title"],
                "points": [
                    {"content": p.content, "kp_type": p.kp_type, "source_type": p.source_type}
                    for p in page_data["points"]
                ],
            },
        )


class MultimodalRecognizer(Recognizer):
    def __init__(self):
        self.api_key = settings.model_api_key
        self.base_url = settings.model_base_url
        self.model_name = settings.model_name
        self.timeout = settings.model_timeout_seconds
        self.max_retry = settings.model_max_retry

    def recognize(self, page_no: int, file_path: str) -> RecognitionResult:
        if not self.api_key:
            return MockRecognizer().recognize(page_no, file_path)

        import base64
        file_path_obj = Path(file_path)
        ext = file_path_obj.suffix.lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".pdf": "application/pdf"}
        mime = mime_map.get(ext, "image/jpeg")

        with open(file_path_obj, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请识别这张PPT照片的内容，提取标题和知识点要点。"},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    ],
                }
            ],
            "max_tokens": 2000,
        }

        for attempt in range(self.max_retry + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(
                        f"{self.base_url}/chat/completions",
                        json=payload,
                        headers={"Authorization": f"Bearer {self.api_key}"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"]
                    confidence = 0.90
                    low_conf = confidence < settings.low_confidence_threshold
                    return RecognitionResult(
                        text=text,
                        confidence=confidence,
                        low_confidence=low_conf,
                        structured={"title": f"页面{page_no}", "points": []},
                    )
            except httpx.TimeoutException:
                if attempt < self.max_retry:
                    continue
                raise ModelTimeoutError()
            except Exception as e:
                if attempt < self.max_retry:
                    continue
                raise RecognitionFailedError(str(e))

        raise RecognitionFailedError("重试次数耗尽")


class FallbackRecognizer(Recognizer):
    def recognize(self, page_no: int, file_path: str) -> RecognitionResult:
        return RecognitionResult(
            text="[识别服务不可用，使用兜底结果]",
            confidence=0.0,
            low_confidence=True,
            structured={"title": f"页面{page_no}", "points": []},
        )


def get_recognizer() -> Recognizer:
    provider = settings.model_provider.lower()
    if provider == "multimodal":
        return MultimodalRecognizer()
    elif provider == "fallback":
        return FallbackRecognizer()
    else:
        return MockRecognizer()