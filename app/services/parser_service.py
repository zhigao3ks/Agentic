"""解析调度服务：根据文件类型选择解析器。"""

from app.core.exceptions import ValidationException
from app.services.parsers.csv_parser import parse_csv
from app.services.parsers.docx_parser import parse_docx
from app.services.parsers.excel_parser import parse_xlsx
from app.services.parsers.md_parser import parse_markdown
from app.services.parsers.models import ParsedDocument
from app.services.parsers.pdf_parser import parse_pdf
from app.services.parsers.txt_parser import parse_txt

_PARSER_MAP = {
    "pdf": parse_pdf,
    "docx": parse_docx,
    "md": parse_markdown,
    "txt": parse_txt,
    "csv": parse_csv,
    "xlsx": parse_xlsx,
}


def parse_document(file_path: str, file_type: str) -> ParsedDocument:
    parser = _PARSER_MAP.get(file_type)
    if not parser:
        raise ValidationException(detail=f"No parser for file type: {file_type}")
    return parser(file_path)
