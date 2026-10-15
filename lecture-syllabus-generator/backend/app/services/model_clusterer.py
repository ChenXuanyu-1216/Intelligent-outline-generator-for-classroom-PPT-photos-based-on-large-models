"""Model assigns request-local IDs; original knowledge points stay authoritative."""

import json

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import settings
from app.errors import AppError, ClusteringFailedError, ModelTimeoutError
from app.prompts_loader import get_prompt_text
from app.services.clusterer import ClusterModule, numbered_title
from app.services.extractor import ExtractedKnowledgePoint


class ModuleAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    title: str = Field(min_length=1, max_length=120)
    point_ids: list[str] = Field(min_length=1)

    @field_validator("title")
    @classmethod
    def single_line_title(cls, value: str) -> str:
        title = value.strip()
        if not title or any(ord(c) < 32 or c in "\x7f\x85\u2028\u2029" for c in value):
            raise ValueError("Module title must be nonempty and on one line")
        return title


class ClusterAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    modules: list[ModuleAssignment] = Field(min_length=1)


class ModelClusterer:
    def cluster(self, points: list[ExtractedKnowledgePoint], page_titles: dict[int, str]) -> list[ClusterModule]:
        if not points:
            return []
        if not settings.model_api_key.strip():
            raise AppError(
                "CLUSTER_CONFIG_ERROR", "模型聚类需要配置 APP_MODEL_API_KEY，或将 APP_CLUSTER_PROVIDER 改为 rule。",
                retryable=False, status_code=503,
            )
        try:
            prompt = get_prompt_text("cluster")
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError("Prompt must be a nonempty string")
        except (OSError, UnicodeError, yaml.YAMLError, AttributeError, TypeError, ValueError):
            raise AppError(
                "CLUSTER_CONFIG_ERROR", "聚类提示词无效或无法读取，请检查 cluster.yaml。", status_code=503,
            ) from None

        point_map = {f"kp_{i}": point for i, point in enumerate(points, 1)}
        supplied = {"points": [
            {
                "id": point_id,
                "content": point.content,
                "kp_type": point.kp_type,
                "page_titles": [page_titles.get(int(page[1:]), page) for page in point.source_pages.split(",")],
            }
            for point_id, point in point_map.items()
        ]}
        payload = {
            "model": settings.model_name,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(supplied, ensure_ascii=False)},
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 4000,
        }
        response = self._request(payload)
        try:
            choice = response.json()["choices"][0]
            if choice.get("finish_reason") == "length":
                raise ValueError("Truncated assignment")
            assignment = ClusterAssignment.model_validate(json.loads(choice["message"]["content"]))
        except (ValueError, TypeError, KeyError, IndexError, AttributeError):
            raise ClusteringFailedError("模型聚类返回格式无效或内容不完整，请重试。") from None

        assigned = [point_id for module in assignment.modules for point_id in module.point_ids]
        if len(assigned) != len(set(assigned)) or set(assigned) != set(point_map):
            raise ClusteringFailedError("模型聚类包含未知、重复或遗漏的知识点 ID，请重试。")

        modules = []
        for index, module in enumerate(assignment.modules, 1):
            original_points = [point_map[point_id] for point_id in module.point_ids]
            pages = {page for point in original_points for page in point.source_pages.split(",")}
            modules.append(ClusterModule(
                title=numbered_title(module.title, index),
                knowledge_points=original_points,
                source_pages=",".join(sorted(pages, key=lambda page: int(page[1:]))),
            ))
        return modules

    def _request(self, payload: dict) -> httpx.Response:
        # Retry transport failures and transient statuses only; never hide errors
        # behind rule-based output or expose provider response bodies to users.
        for attempt in range(max(0, settings.model_max_retry) + 1):
            try:
                with httpx.Client(timeout=settings.model_timeout_seconds) as client:
                    response = client.post(
                        f"{settings.model_base_url.strip().rstrip('/')}/chat/completions",
                        json=payload,
                        headers={"Authorization": f"Bearer {settings.model_api_key.strip()}"},
                    )
                    response.raise_for_status()
                    return response
            except httpx.TimeoutException:
                if attempt < settings.model_max_retry:
                    continue
                raise ModelTimeoutError() from None
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                retryable = status in {408, 429} or status >= 500
                if retryable and attempt < settings.model_max_retry:
                    continue
                raise ClusteringFailedError(
                    f"模型聚类服务返回 HTTP {status}，请检查模型配置或稍后重试。", retryable=retryable,
                ) from None
            except httpx.TransportError:
                if attempt < settings.model_max_retry:
                    continue
                raise ClusteringFailedError("无法连接模型聚类服务，请检查连接后重试。") from None
            except httpx.InvalidURL:
                raise AppError("CLUSTER_CONFIG_ERROR", "模型服务地址无效，请检查 APP_MODEL_BASE_URL。", status_code=503) from None
        raise ClusteringFailedError()
