"""测试 app/services/text_cleaner.py"""

from app.services.text_cleaner import clean_text, estimate_tokens


class TestCleanText:
    def test_removes_control_characters(self):
        text = "Hello\x00\x01World"
        result = clean_text(text)
        assert "\x00" not in result
        assert "Hello" in result

    def test_unifies_line_endings(self):
        text = "line1\r\nline2\rline3"
        result = clean_text(text)
        assert "\r\n" not in result
        assert "\r" not in result
        assert result == "line1\nline2\nline3"

    def test_collapses_multiple_blank_lines(self):
        text = "para1\n\n\n\n\npara2"
        result = clean_text(text)
        assert result == "para1\n\npara2"

    def test_strips_trailing_whitespace(self):
        text = "  hello world  \n  line2  "
        result = clean_text(text)
        assert result == "hello world\nline2"

    def test_empty_text(self):
        assert clean_text("") == ""
        assert clean_text("   \n\n  ") == ""

    def test_preserves_paragraph_structure(self):
        text = "第一章  概述\n\n  这是第一段内容。\n这是同一段的另一句。\n\n第二章  方法\n\n实验使用了标准方法。"
        result = clean_text(text)
        assert "第一章" in result and "概述" in result
        assert "第二章" in result and "方法" in result
        assert "这是第一段内容。" in result


class TestEstimateTokens:
    def test_chinese_text(self):
        tokens = estimate_tokens("这是一段中文文本用于测试")
        assert tokens > 0

    def test_english_text(self):
        tokens = estimate_tokens("This is some English text for testing")
        assert tokens > 0

    def test_mixed_text(self):
        tokens = estimate_tokens("中英mixed文本text")
        assert tokens > 0
