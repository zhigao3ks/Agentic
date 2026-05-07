"""解析结果数据模型。"""

from dataclasses import dataclass, field


@dataclass
class ParsedDocument:
    text: str
    pages: list[dict] = field(default_factory=list)
    sections: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
