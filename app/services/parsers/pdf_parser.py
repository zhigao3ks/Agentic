"""PDF 解析器。"""

import fitz  # PyMuPDF

from app.services.parsers.models import ParsedDocument


class PDFParser:
    @staticmethod
    def parse(file_path: str) -> ParsedDocument:
        doc = fitz.open(file_path)
        pages = []
        full_text_parts = []

        for i, page in enumerate(doc):
            text = page.get_text("text")
            full_text_parts.append(text)
            pages.append({"page_num": i + 1, "text": text})

        metadata = {}
        if doc.metadata:
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "page_count": len(doc),
            }

        doc.close()
        return ParsedDocument(
            text="\n\n".join(full_text_parts),
            pages=pages,
            metadata=metadata,
        )


def parse_pdf(file_path: str) -> ParsedDocument:
    return PDFParser.parse(file_path)
