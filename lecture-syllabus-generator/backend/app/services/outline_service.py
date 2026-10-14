from app.services.clusterer import ClusterModule


class OutlineService:
    def render_markdown(self, modules: list[ClusterModule]) -> str:
        lines = ["# 课程大纲", ""]
        for module in modules:
            lines.append(f"## {module.title}")
            for kp in module.knowledge_points:
                source_tag = f"（来源：{kp.source_pages}）"
                type_tag = f"【{kp.source_type}】"
                lines.append(f"- {kp.content}{source_tag}{type_tag}")
            lines.append("")
        return "\n".join(lines).strip()

    def parse_markdown(self, markdown: str) -> list[dict]:
        modules = []
        current_module = None
        for line in markdown.strip().split("\n"):
            if line.startswith("## "):
                if current_module:
                    modules.append(current_module)
                current_module = {"title": line[3:].strip(), "points": []}
            elif line.startswith("- ") and current_module is not None:
                content = line[2:].strip()
                source_pages = ""
                source_type = ""
                if "（来源：" in content:
                    idx = content.rfind("（来源：")
                    end = content.rfind("）")
                    if end > idx:
                        source_pages = content[idx + 4:end]
                        content = content[:idx] + content[end + 1:]
                if "【" in content and "】" in content:
                    s = content.rfind("【")
                    e = content.rfind("】")
                    if e == len(content) - 1 and content[s + 1:e] in {"课堂原话", "AI推断", "来源待核对"}:
                        source_type = content[s + 1:e]
                        content = content[:s] + content[e + 1:]
                current_module["points"].append({
                    "content": content.strip(),
                    "source_pages": source_pages,
                    "source_type": source_type,
                })
        if current_module:
            modules.append(current_module)
        return modules


outline_service = OutlineService()
