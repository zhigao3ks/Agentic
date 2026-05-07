"""上下文构造器 —— 将检索结果格式化为 LLM prompt。"""

MAX_CONTEXT_CHARS = 4000


def build_context(
    chunks: list[dict],
    max_chars: int = MAX_CONTEXT_CHARS,
) -> str:
    """将检索到的 chunk 列表构造为带编号的上下文文本。"""
    if not chunks:
        return "未找到相关文档。"

    parts = []
    total = 0
    for i, ch in enumerate(chunks):
        meta = ch.get("metadata", {})
        content = meta.get("content", "") if "content" in meta else ch.get("content", "")
        source = meta.get("section_title", "") or ch.get("id", "")

        prefix = f"[{i + 1}]"
        if source:
            prefix += f" ({source})"

        snippet = f"{prefix}\n{content}"

        if total + len(snippet) > max_chars and parts:
            break

        parts.append(snippet)
        total += len(snippet)

    return "\n\n".join(parts)
