"""Markdown 解析器。"""

from app.services.parsers.models import ParsedDocument


class MarkdownParser:
    @staticmethod
    def parse(file_path: str) -> ParsedDocument:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        sections = []
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                level = len(stripped) - len(stripped.lstrip("#"))
                title = stripped.lstrip("#").strip()
                if title:
                    sections.append({"title": title, "level": min(level, 6)})

        return ParsedDocument(
            text=content,
            sections=sections,
            metadata={"format": "markdown"},
        )


def parse_markdown(file_path: str) -> ParsedDocument:
    return MarkdownParser.parse(file_path)
