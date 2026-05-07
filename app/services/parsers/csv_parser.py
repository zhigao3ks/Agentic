"""CSV 解析器。"""

import csv

from app.services.parsers.models import ParsedDocument

_MAX_ROWS = 10000


class CSVParser:
    @staticmethod
    def parse(file_path: str) -> ParsedDocument:
        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = []
            for i, row in enumerate(reader):
                if i >= _MAX_ROWS:
                    break
                rows.append(" | ".join(row))

        return ParsedDocument(
            text="\n".join(rows),
            metadata={"format": "csv", "row_count": len(rows)},
        )


def parse_csv(file_path: str) -> ParsedDocument:
    return CSVParser.parse(file_path)
