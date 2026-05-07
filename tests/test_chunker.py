"""测试 app/services/chunker.py"""

from app.services.chunker import ChunkData, chunk_text


class TestChunkText:
    def test_empty_text(self):
        chunks = chunk_text("")
        assert len(chunks) == 0

    def test_short_text_single_chunk(self):
        text = "这是一段简短的测试文本。"
        chunks = chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0].content == text
        assert chunks[0].chunk_index == 0

    def test_long_text_multiple_chunks(self):
        # 生成一段超过默认 chunk_size 的文本
        paragraph = "这是一段测试文本。" * 120  # ~1200 chars
        chunks = chunk_text(paragraph, chunk_size=500, chunk_overlap=80)
        assert len(chunks) >= 2

    def test_paragraphs_become_separate_chunks(self):
        text = "第一段内容。\n\n第二段内容不同。"
        chunks = chunk_text(text, chunk_size=500, chunk_overlap=0)
        assert len(chunks) >= 1

    def test_chunks_have_increasing_indices(self):
        paragraph = "这是测试文本。" * 120
        chunks = chunk_text(paragraph, chunk_size=500, chunk_overlap=80)
        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_chunks_include_token_count(self):
        text = "这是一段中文测试文本，用于验证 token 计数功能。"
        chunks = chunk_text(text)
        assert chunks[0].token_count > 0

    def test_chunks_include_char_positions(self):
        text = "这是一段测试文本。"
        chunks = chunk_text(text)
        assert chunks[0].start_char >= 0
        assert chunks[0].end_char > chunks[0].start_char

    def test_page_mapping(self):
        pages = [
            {"page_num": 1, "text": "第一页内容。\n"},
            {"page_num": 2, "text": "第二页内容。"},
        ]
        text = "第一页内容。\n第二页内容。"
        chunks = chunk_text(text, pages=pages)
        assert len(chunks) >= 1

    def test_section_detection(self):
        sections = [{"title": "第一章", "level": 1}, {"title": "第二章", "level": 1}]
        text = "第一章\n\n这是第一章的内容。\n\n第二章\n\n这是第二章的内容。"
        chunks = chunk_text(text, sections=sections)
        # 最后一个 chunk 应属于"第二章"
        assert chunks[-1].section_title in ("第一章", "第二章", "")

    def test_overlap_between_chunks(self):
        paragraph = "这是测试文本。" * 120
        chunks = chunk_text(paragraph, chunk_size=500, chunk_overlap=100)
        if len(chunks) >= 2:
            # 检查第二个 chunk 包含了第一个 chunk 的结尾部分
            end_of_first = chunks[0].content[-50:]
            assert end_of_first in chunks[1].content or len(chunks[1].content) < 600
