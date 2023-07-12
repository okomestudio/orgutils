"""Org structures."""
from dataclasses import dataclass
from typing import List


@dataclass
class OrgObject:  # noqa
    def render(self) -> List[str]:  # noqa
        raise NotImplementedError


@dataclass
class OrgFile(OrgObject):  # noqa
    title: str
    properties: dict


@dataclass
class Heading(OrgObject):  # noqa
    title: str
    level: int
    properties: dict

    def render(self) -> List[str]:  # noqa
        lines = []
        lines.append("*" * self.level + " " + self.title)
        if self.properties:
            lines.append(":PROPERTIES:")
            for k, v in self.properties.items():
                lines.append(f":{ k.upper() }: { v }")
            lines.append(":END:")
        return lines


@dataclass
class Paragraph(OrgObject):  # noqa
    content: str

    def render(self):  # noqa
        return [self.content]


@dataclass
class Block(OrgObject):  # noqa
    content: str


@dataclass
class QuoteBlock(Block):  # noqa
    def render(self) -> List[str]:  # noqa
        lines = []
        lines.append("#+BEGIN_QUOTE")
        lines.append(self.content)
        lines.append("#+END_QUOTE")
        return lines
