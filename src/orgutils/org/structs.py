"""Org structures."""
from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class OrgObject:
    def render(self) -> List[str]:
        raise NotImplementedError


@dataclass
class OrgFile(OrgObject):
    title: str
    properties: dict


@dataclass
class Heading(OrgObject):
    title: str
    level: int
    properties: dict

    def render(self) -> List[str]:
        lines = []
        lines.append("*" * self.level + " " + self.title)
        if self.properties:
            lines.append(":PROPERTIES:")
            for k, v in self.properties.items():
                lines.append(f":{ k.upper() }: { v }")
            lines.append(":END:")
        return lines


@dataclass
class Paragraph(OrgObject):
    content: str

    def render(self) -> List[str]:
        return [self.content]


@dataclass
class Block(OrgObject):
    content: str


@dataclass
class QuoteBlock(Block):
    def render(self) -> List[str]:
        lines = []
        lines.append("#+BEGIN_QUOTE")
        lines.append(self.content)
        lines.append("#+END_QUOTE")
        return lines


@dataclass
class Group(OrgObject):
    objects: List[OrgObject]

    def render(self) -> List[str]:
        lines = []
        for obj in self.objects:
            lines.extend(obj.render())
        return lines


def dumps(org_objects: Iterable[OrgObject]) -> str:
    lines = []
    for org_object in org_objects:
        lines.extend(org_object.render() + [""])
    return "\n".join(lines)
