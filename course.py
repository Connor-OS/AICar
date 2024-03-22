import numpy as np
from random import choice
from operator import add
from operator import sub


def generate_course(grid_size) -> np.array:
    """This function generates a course which is essentially a random walk around a grid space starting and ending in
    the same space it returns a grid with the layout of the course encoded into it"""

    start = (int(grid_size / 2), 0)
    next = (int(grid_size / 2) + 1, 0)
    end = (int(grid_size / 2) - 1, 0)

    course = [start, next]
    current = next
    steps = [[1, 0], [-1, 0], [0, 1], [0, -1]]
    dead_ends = []

    # Run a random walk through the course space
    while current != end:
        available_steps = []

        for step in steps:
            next = tuple(map(add, current, step))
            if next in course or next in dead_ends:
                continue
            if -1 in next or grid_size in next:
                continue
            available_steps.append(next)

        if not available_steps:
            # hit a dead end
            dead_ends.append(course.pop())
            current = course[-1]
        else:
            current = choice(available_steps)
            course.append(current)

    # encode the course into a grid that can be interpreted as unique pieces
    grid = np.zeros((grid_size, grid_size))

    for i, step in enumerate(course):
        connections = [tuple(map(sub, step, course[i - 1])),
                       tuple(map(sub, step, course[(i + 1) % len(course)]))]
        for con in connections:
            if con[0] == 1:
                grid[step] += 1
            elif con[1] == -1:
                grid[step] += 2
            elif con[0] == -1:
                grid[step] += 4
            elif con[1] == 1:
                grid[step] += 8

            else:
                raise Exception


    return grid, course


if __name__ == "__main__":
    print("OI")
    generate_course(12)
