"""文本清洗工具。"""

import re


def clean_text(text: str) -> str:
    """清洗文本：合并多余空白，移除控制字符，保留结构。"""
    # 移除零宽字符和不可见控制字符（保留 \n \t）
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    # 统一换行为 \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # 合并 3 个以上连续换行为 2 个（保留段落分隔）
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 去除行首行尾空白（保留换行结构）
    lines = [line.strip() for line in text.split("\n")]
    # 合并连续的完全空行
    result = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                result.append("")
            prev_empty = True
        else:
            result.append(line)
            prev_empty = False
    return "\n".join(result).strip()


def estimate_tokens(text: str) -> int:
    """估算 token 数量（中文约 2 字符/token，英文约 4 字符/token）。"""
    chinese_chars = len(re.findall(r"[一-鿿]", text))
    other_chars = len(text) - chinese_chars
    return int(chinese_chars / 1.5 + other_chars / 4)
