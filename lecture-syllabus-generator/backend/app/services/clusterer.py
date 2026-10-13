from dataclasses import dataclass, field
from app.services.extractor import ExtractedKnowledgePoint


@dataclass
class ClusterModule:
    title: str
    knowledge_points: list[ExtractedKnowledgePoint] = field(default_factory=list)
    source_pages: str = ""


class Clusterer:
    def cluster(self, points: list[ExtractedKnowledgePoint], page_titles: dict[int, str]) -> list[ClusterModule]:
        if not points:
            return []

        page_to_points: dict[int, list[ExtractedKnowledgePoint]] = {}
        for kp in points:
            primary_page = int(kp.source_pages.split(",")[0][1:])
            page_to_points.setdefault(primary_page, []).append(kp)

        modules = []
        sorted_pages = sorted(page_to_points.keys())
        for idx, page_no in enumerate(sorted_pages, 1):
            title = page_titles.get(page_no, f"模块{idx}")
            if not title.startswith(("一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、", "十、")):
                cn_nums = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
                num_prefix = cn_nums[idx - 1] if idx <= len(cn_nums) else str(idx)
                title = f"{num_prefix}、{title}"

            kps = page_to_points[page_no]
            all_pages = set()
            for kp in kps:
                for p in kp.source_pages.split(","):
                    all_pages.add(p)
            source_pages = ",".join(sorted(all_pages, key=lambda x: int(x[1:])))

            modules.append(ClusterModule(
                title=title,
                knowledge_points=kps,
                source_pages=source_pages,
            ))

        return modules