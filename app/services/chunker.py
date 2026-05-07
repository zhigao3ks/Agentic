"""结构化文档切片器。"""

import re
from dataclasses import dataclass, field

from app.core.config import settings

# 默认参数
DEFAULT_CHUNK_SIZE = 800       # 字符数
DEFAULT_CHUNK_OVERLAP = 120    # 字符数
MIN_CHUNK_SIZE = 100           # 最小 chunk 字符数（低于此不单独成 chunk）


@dataclass
class ChunkData:
    content: str
    page: int | None = None
    section_title: str = ""
    chunk_index: int = 0
    start_char: int = 0
    end_char: int = 0
    token_count: int = 0


def chunk_text(
    text: str,
    pages: list[dict] | None = None,
    sections: list[dict] | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[ChunkData]:
    """将文本切分为结构化 chunk 列表。"""
    if not text.strip():
        return []

    # 构建字符→页码映射
    char_to_page = _build_page_map(text, pages or [])

    # 构建章节边界
    section_boundaries = _build_section_boundaries(text, sections or [])

    # 按段落切分
    paragraphs = _split_paragraphs(text)

    # 合并段落为 chunk
    chunks = _merge_paragraphs_to_chunks(
        paragraphs, section_boundaries, char_to_page, chunk_size, chunk_overlap
    )

    # 编号和生成元数据
    for i, chunk in enumerate(chunks):
        chunk.chunk_index = i
        chunk.token_count = _estimate_tokens(chunk.content)
        chunk.page = char_to_page.get(chunk.start_char)
        # 找到最近的 section
        chunk.section_title = _find_section(chunk.start_char, section_boundaries)

    return chunks


def _build_page_map(text: str, pages: list[dict]) -> dict[int, int | None]:
    """构建字符偏移→页码的映射。"""
    char_map = {}
    offset = 0
    for p in pages:
        page_num = p.get("page_num")
        page_text = p.get("text", "")
        for i in range(len(page_text)):
            char_map[offset + i] = page_num
        offset += len(page_text)
        # 页面之间的分隔符（如果有的话）
        char_map[offset] = page_num
        offset += 1
    return char_map


def _build_section_boundaries(text: str, sections: list[dict]) -> list[tuple[int, str]]:
    """找到每个章节标题在文本中的位置。"""
    boundaries = []
    for sec in sections:
        title = sec.get("title", "")
        if title:
            pos = text.find(title)
            if pos >= 0:
                boundaries.append((pos, title))
    boundaries.sort()
    return boundaries


def _split_paragraphs(text: str) -> list[tuple[str, int]]:
    """将文本按段落切分，返回 (段落文本, 起始位置)。"""
    paragraphs = []
    # 按双换行或单换行分段
    for para in re.split(r"\n\n+", text):
        para = para.strip()
        if para:
            pos = text.find(para) if para else 0
            paragraphs.append((para, pos))
    return paragraphs


def _merge_paragraphs_to_chunks(
    paragraphs: list[tuple[str, int]],
    section_boundaries: list[tuple[int, str]],
    char_to_page: dict[int, int | None],
    chunk_size: int,
    chunk_overlap: int,
) -> list[ChunkData]:
    """将段落合并为 chunk，保持结构和重叠。"""
    chunks: list[ChunkData] = []
    buffer = ""
    buffer_start = 0
    buffer_end = 0

    def flush(final: bool = False) -> None:
        nonlocal buffer, buffer_start, buffer_end
        if buffer and (final or len(buffer) >= MIN_CHUNK_SIZE):
            chunks.append(ChunkData(
                content=buffer,
                start_char=buffer_start,
                end_char=buffer_end,
            ))
        buffer = ""
        buffer_start = 0

    for para_text, para_pos in paragraphs:
        # 如果单个段落超过 chunk_size，需要进一步切分
        if len(para_text) > chunk_size:
            flush()
            _split_long_paragraph(para_text, para_pos, chunks, chunk_size, chunk_overlap)
            continue

        # 检查是否加上当前段落会超过 chunk_size
        if buffer and len(buffer) + len(para_text) + 2 > chunk_size:
            flush()

        if not buffer:
            buffer_start = para_pos
        buffer = (buffer + "\n\n" + para_text) if buffer else para_text
        buffer_end = para_pos + len(para_text)

    flush(final=True)

    # 添加重叠：每个 chunk 末尾 N 个字符作为下一个 chunk 的前缀
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped = []
        for i, ch in enumerate(chunks):
            if i > 0:
                prev_end = chunks[i - 1].content[-chunk_overlap:]
                ch.content = prev_end + "\n" + ch.content
            overlapped.append(ch)
        chunks = overlapped

    return chunks


def _split_long_paragraph(
    para_text: str,
    para_pos: int,
    chunks: list[ChunkData],
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    """将一个过长的段落切分为多个 chunk，优先按句子边界切分。"""
    sentences = re.split(r"(?<=[。！？!?\n])\s*", para_text)
    buffer = ""
    buf_start = para_pos

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        if len(buffer) + len(sent) > chunk_size and len(buffer) >= MIN_CHUNK_SIZE:
            sent_pos = para_text.find(sent, buf_start - para_pos)
            chunks.append(ChunkData(
                content=buffer,
                start_char=buf_start,
                end_char=buf_start + len(buffer),
            ))
            # 重叠
            overlap_text = buffer[-chunk_overlap:] if len(buffer) > chunk_overlap else buffer
            buffer = overlap_text + " " + sent
            buf_start = buf_start + len(buffer) - len(overlap_text) - len(sent) - 1
        else:
            buffer = (buffer + " " + sent).strip() if buffer else sent

    if buffer:
        chunks.append(ChunkData(
            content=buffer,
            start_char=buf_start,
            end_char=buf_start + len(buffer),
        ))


def _find_section(char_pos: int, boundaries: list[tuple[int, str]]) -> str:
    """找到字符位置所属的章节标题。"""
    current = ""
    for pos, title in boundaries:
        if pos <= char_pos:
            current = title
        else:
            break
    return current


def _estimate_tokens(text: str) -> int:
    chinese = len(re.findall(r"[一-鿿]", text))
    other = len(text) - chinese
    return int(chinese / 1.5 + other / 4)
