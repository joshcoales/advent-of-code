import dataclasses
from functools import cached_property
from typing import List

from utils import load_lines
from utils_coords import Coords2D


class Map:
    def __init__(self, width: int, height: int) -> None:
        self.map = []
        for _ in range(height):
            self.map.append([0 for _ in range(width)])

    def render(self) -> str:
        return "\n".join(
            "".join(str(val) or "." for val in row)
            for row in self.map
        )

    def num_overlaps(self, min_overlap: int = 2) -> int:
        return sum(
            sum(1 if val >= min_overlap else 0 for val in row)
            for row in self.map
        )

    def add_line(self, line: "Line") -> None:
        if line.vertical:
            for y in range(line.min_y, line.max_y + 1):
                self.map[y][line.start.x] += 1
            return
        if line.horizontal:
            for x in range(line.min_x, line.max_x + 1):
                self.map[line.start.y][x] += 1
            return
        raise NotImplementedError


@dataclasses.dataclass
class Line:
    start: Coords2D
    end: Coords2D

    @cached_property
    def min_x(self) -> int:
        return min(self.start.x, self.end.x)

    @cached_property
    def min_y(self) -> int:
        return min(self.start.y, self.end.y)

    @cached_property
    def max_x(self) -> int:
        return max(self.start.x, self.end.x)

    @cached_property
    def max_y(self) -> int:
        return max(self.start.y, self.end.y)

    @cached_property
    def horizontal(self) -> bool:
        return self.start.y == self.end.y

    @cached_property
    def vertical(self) -> bool:
        return self.start.x == self.end.x

    def is_valid(self) -> bool:
        return self.horizontal or self.vertical

    @classmethod
    def from_input_line(cls, input_line: str) -> "Line":
        start, end = input_line.split(" -> ", 1)
        return cls(
            Coords2D.from_input_line(start),
            Coords2D.from_input_line(end)
        )


def find_map_dimensions(lines: List[Line]) -> Coords2D:
    max_x = 0
    max_y = 0
    for line in lines:
        max_x = max(max_x, line.max_x)
        max_y = max(max_y, line.max_y)
    return Coords2D(max_x + 1, max_y + 1)


if __name__ == "__main__":
    my_input = load_lines()
    vent_lines = [Line.from_input_line(l) for l in my_input]
    dimensions = find_map_dimensions(vent_lines)
    my_map = Map(dimensions.x, dimensions.y)
    for vent_line in vent_lines:
        if vent_line.is_valid():
            my_map.add_line(vent_line)
    print(my_map.render())
    print(my_map.num_overlaps())