"""TXT 解析器。"""

from app.services.parsers.models import ParsedDocument


class TxtParser:
    @staticmethod
    def parse(file_path: str) -> ParsedDocument:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        return ParsedDocument(
            text=content,
            metadata={"format": "text"},
        )


def parse_txt(file_path: str) -> ParsedDocument:
    return TxtParser.parse(file_path)
