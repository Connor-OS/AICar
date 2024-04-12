#!/usr/bin/env python3
"""Car racing game written in Python.

This module implements a simple car driving game in Python using the Pygame engine.

"""

import math
import time

import pygame
import numpy as np

from course import generate_course
from recorder import PygameRecord

# Game Configuration
SCREEN_SIZE = (800, 800)
GRID_SIZE = 6
BOX_SIZE = SCREEN_SIZE[0] / GRID_SIZE
SCREEN_DISPLAY_CAPTION = 'Vector Racing'
SPLASH_SCREEN_TIME = 5
SPLASH_SCREEN_IMAGE_FILENAME = 'Shrek.png'
HUMAN_PLAYER_IMAGE_FILENAME = 'human-player-racecar.png'
COMPUTER_PLAYER_IMAGE_FILENAME = 'computer-player-racecar.png'
HUMAN_PLAYER_IMAGE_SIZE = (25, 50)
COMPUTER_PLAYER_IMAGE_SIZE = (10, 20)
COMPUTER_PLAYER_COUNT = 0
MESSAGE_FONT = 'freesansbold.ttf'
MESSAGE_FONT_SIZE = 25
MESSAGE_GAME_OVER = 'You Crashed! Your score was: '
CLOCK_FPS = 60
DELTA_X_LEFT_CONSTANT = -5
DELTA_X_RIGHT_CONSTANT = 5

# Colors
BLACK = (0, 0, 0)
GREY = (211, 211, 211)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


class Car:

    def __init__(self, pos_x=int(SCREEN_SIZE[0] / 2), pos_y=int(BOX_SIZE * 0.5), delta_x=0,
                 delta_y=0, theta=90, delta_theta=0, brain=None):
        """Initialise a car object.

        Args:
            pos_x (int): The position of the car on the x-plane.
            pos_y (int): The position of the car on the y-plane.
            delta_x (int): The amount by which to move the car on the x-plane.
            delta_y (int): The amount by which to move the car on the y-plane.
            human (bool): Whether the car is a human player or not.

        """

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.x_box = pos_x / BOX_SIZE
        self.y_box = pos_y / BOX_SIZE
        self.theta = theta
        self.delta_theta = delta_theta
        self.image = None
        self.bounding_box = None
        self.aa_bounding_box = None
        self.rays = np.zeros(5)
        self.current_box = 0
        self.brain = brain

    def load_transform_image(self):
        """Load the car image from the filesystem."""

        self.image = pygame.image.load(
            HUMAN_PLAYER_IMAGE_FILENAME).convert()
        self.image.set_colorkey(BLACK)
        self.image = pygame.transform.scale(
            self.image, HUMAN_PLAYER_IMAGE_SIZE)

    def render_image(self):
        """Render the car image on the display."""
        rotated_image = pygame.transform.rotate(self.image, self.theta)
        self.bounding_box = rotated_image.get_rect(center=self.image.get_rect(topleft=[self.pos_x, self.pos_y]).center)
        screen.blit(rotated_image, self.bounding_box)

    def turn_left_right(self):
        """Move the car on the x-plane by delta x."""
        self.theta += self.delta_theta

    def move_up_down(self):
        """Move the car on the y-plane by delta y."""
        if self.brain:
            self.pos_x += -4 * math.sin(self.theta / 180 * math.pi)
            self.pos_y += -4 * math.cos(self.theta / 180 * math.pi)
        else:
            self.pos_x += self.delta_y * math.sin(self.theta / 180 * math.pi)
            self.pos_y += self.delta_y * math.cos(self.theta / 180 * math.pi)

    def check_score_accumulated(self, course):
        score = 0

        current = course.path[self.current_box % len(course.path)]
        # pygame.draw.rect(screen, GREEN, [current[0]*BOX_SIZE, current[1]*BOX_SIZE, BOX_SIZE, BOX_SIZE])

        if pygame.Rect(current[0]*BOX_SIZE, current[1]*BOX_SIZE, BOX_SIZE, BOX_SIZE).collidepoint(self.pos_x, self.pos_y):
            self.current_box += 1
            score += 1
        return score

    def shoot_rays(self, course):
        """
        shoot rays out and measure there distance to nearest wall intersection
        """

        x, y = self.bounding_box.center

        ray_len = 500

        targets = [(x - ray_len * math.sin(math.radians(self.theta - 90)), y - ray_len * math.cos(math.radians(self.theta - 90))),
                (x - ray_len * math.sin(math.radians(self.theta - 45)), y - ray_len * math.cos(math.radians(self.theta - 45))),
                (x - ray_len * math.sin(math.radians(self.theta)), y - ray_len * math.cos(math.radians(self.theta))),
                (x - ray_len * math.sin(math.radians(self.theta + 45)), y - ray_len * math.cos(math.radians(self.theta + 45))),
                (x - ray_len * math.sin(math.radians(self.theta + 90)), y - ray_len * math.cos(math.radians(self.theta + 90)))]

        for i, target in enumerate(targets):
            ray = ray_len
            # pygame.draw.line(screen, RED, (x, y), target)
            point = None
            for line in course.lines:
                if p := get_intersection((x, y), target, *line):
                    dist = ((x - p[0])**2 + (y - p[1])**2)**0.5
                    if dist < ray:
                        ray = dist
                        point = p
            if point:
                self.rays[i] = ray
                pygame.draw.circle(screen, RED, (point[0], point[1]), 10, 2)
                pygame.draw.line(screen, RED, (x, y), (point[0], point[1]))
            else:
                #This should never happen, need to fix bug in get_intersection
                self.rays[i] = 0


def gradient(p1, p2):
    if p1[0] == p2[0]:
        return None
    return (p1[1] - p2[1]) / (p1[0] - p2[0])


def Yintercept(p, m):
    return p[1] - (m * p[0])


def get_intersection(p1, p2, p3, p4):
    """Calculate the intersection of two lines defined by two pairs of points"""
    p1, p2 = min(p1, p2), max(p1, p2)
    p3, p4 = min(p3, p4), max(p3, p4)

    m1 = gradient(p1, p2)
    m2 = gradient(p3, p4)

    if m1 == m2:
        return None

    if m1 is not None and m2 is not None:
        c1 = Yintercept(p1, m1)
        c2 = Yintercept(p3, m2)
        # Neither line vertical
        x = (c2 - c1) / (m1 - m2)
        y = (m1 * x) + c1
    else:
        # Line 1 is vertical so use line 2's values
        if m1 is None:
            # TODO: fix bug here where Line one is vertical and a collision is sometimes not picked up
            c2 = Yintercept(p3, m2)
            x = p1[0]
            y = m2 * x + c2
        # Line 2 is vertical so use line 1's values
        elif m2 is None:
            c1 = Yintercept(p1, m1)
            x = p3[0]
            y = m1 * x + c1

    p = (x, y)
    # pygame.draw.circle(screen, RED, (p[0], p[1]), 10, 2)

    tolerance = 1

    if (min(p1[0], p2[0])-tolerance <= x <= max(p1[0], p2[0])+tolerance
            and min(p1[1], p2[1])-tolerance <= y <= max(p1[1], p2[1])+tolerance
            and min(p3[0], p4[0])-tolerance <= x <= max(p3[0], p4[0])+tolerance
            and min(p3[1], p4[1])-tolerance <= y <= max(p3[1], p4[1])+tolerance):
        return p
    else:
        return None


class Course:
    def __init__(self):
        """Initialize the courser"""

        self.lines = []
        self.course_grid, self.path = generate_course(GRID_SIZE)
        self.path = self.path[::-1] # reverse path

    def init_course(self):
        for i_y in range(GRID_SIZE):
            for i_x in range(GRID_SIZE):

                x, y = BOX_SIZE * i_x, BOX_SIZE * i_y

                top = [(x, y), (x + BOX_SIZE, y)]
                bottom = [(x, y + BOX_SIZE), (x + BOX_SIZE, y + BOX_SIZE)]
                right = [(x, y), (x, y + BOX_SIZE)]
                left = [(x + BOX_SIZE, y), (x + BOX_SIZE, y + BOX_SIZE)]

                match self.course_grid[i_x, i_y]:
                    case 5:
                        self.lines.append(top)
                        self.lines.append(bottom)
                    case 10:
                        self.lines.append(right)
                        self.lines.append(left)
                    case 3:
                        self.lines.append(top)
                        self.lines.append(left)
                        pygame.draw.arc(screen, BLACK, [x - BOX_SIZE, y, BOX_SIZE * 2, BOX_SIZE * 2], 0, math.pi / 2)
                    case 6:
                        self.lines.append(top)
                        self.lines.append(right)
                        pygame.draw.arc(screen, BLACK, [x, y, BOX_SIZE * 2, BOX_SIZE * 2], math.pi / 2, math.pi)
                    case 9:
                        self.lines.append(bottom)
                        self.lines.append(left)
                        pygame.draw.arc(screen, BLACK, [x - BOX_SIZE, y - BOX_SIZE, BOX_SIZE * 2, BOX_SIZE * 2],
                                        (3 * math.pi) / 2, 2 * math.pi)
                    case 12:
                        self.lines.append(bottom)
                        self.lines.append(right)
                        pygame.draw.arc(screen, BLACK, [x, y - BOX_SIZE, BOX_SIZE * 2, BOX_SIZE * 2], math.pi,
                                        (3 * math.pi) / 2)

    def render_course(self):
        for line in self.lines:
            pygame.draw.line(screen, BLACK, *line)


def initialize_screen():
    """Return the display with an initial splash screen."""

    # Set the display caption
    pygame.display.set_caption(SCREEN_DISPLAY_CAPTION)

    # Instantiate a new display with the given screen size
    display = pygame.display.set_mode(SCREEN_SIZE)

    return display


def create_human_player():
    """Create a car object that is controlled by the human player."""

    # Create the human player car object
    human_player_car = Car(
        pos_x=int(SCREEN_SIZE[0] / 2),
        pos_y=int(BOX_SIZE * 0.5),
        delta_x=0,
        delta_y=0)

    return human_player_car


def collision_with_course(car, course):
    """Check whether the human car object has exceeded the screen boundaries
    along the x-plane."""

    for line in course.lines:
        if car.bounding_box.clipline(line):
            return True
    return False


def game_over(score):
    """If a collision event has occurred, render a game over message, then reset
    the game parameters before starting a new indefinite game loop after
    a brief pause."""

    # Display the game over message along with the score
    font = pygame.font.Font(MESSAGE_FONT, MESSAGE_FONT_SIZE)
    text = font.render(MESSAGE_GAME_OVER + str(score), True, BLACK)
    text_rectangle = text.get_rect()
    text_rectangle.center = ((SCREEN_SIZE[0] / 2), (SCREEN_SIZE[1] / 2))
    screen.blit(text, text_rectangle)
    pygame.display.update()

    # Pause the application before continuing with a new game loop
    time.sleep(2)
    # Reset the game parameters
    global clock, human_player, collision_event_detected
    clock = pygame.time.Clock()
    human_player = create_human_player()
    collision_event_detected = False
    speed_increment = 2


def indefinite_game_loop(car=create_human_player(), course=Course(), recorder=None):
    """Vector racing game events and subsequent display rendering actions."""

    car.load_transform_image()
    course.init_course()
    score = 0
    start = time.time()

    # ----- FORMULAPY GAME LOOP -----
    while not request_window_close:

        # ----- EVENT DETECTION LOOP -----
        for event in pygame.event.get():

            # Close Window Event
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # Keyboard Key Down Event
            if event.type == pygame.KEYDOWN:

                # Left Key
                if event.key == pygame.K_LEFT:
                    car.delta_theta = 5

                # Right Key
                if event.key == pygame.K_RIGHT:
                    car.delta_theta = -5

                # up Key
                if event.key == pygame.K_UP:
                    car.delta_y += DELTA_X_LEFT_CONSTANT

                # down Key
                if event.key == pygame.K_DOWN:
                    car.delta_y += DELTA_X_RIGHT_CONSTANT

            # Keyboard Key Up Event
            if event.type == pygame.KEYUP:

                # Left or Right Key
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    car.delta_theta = 0

                # Up or Down Key
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    car.delta_y = 0

        # ----- UPDATE DISPLAY -----

        # Fill the display with a white background
        screen.fill(GREY)

        #check score
        if car.check_score_accumulated(course):
            score += 1
            start = time.time()

        # Whilst there is no collision event
        global collision_event_detected

        if not collision_event_detected and (time.time() - start) < 5 and score < 100:

            course.render_course()

            # Render the player car object
            car.render_image()

            # Ask AI what to do
            if car.brain:
                to_do = car.brain.activate(car.rays)
                active_neuron = max(to_do)
                # Turn Left
                if to_do[0] == active_neuron:
                    car.delta_theta = 5
                # Turn Right
                elif to_do[1] == active_neuron:
                    car.delta_theta = -5
                # Turn Right
                elif to_do[2] == active_neuron:
                    car.delta_theta = 0

                # if to_do[2] < 0.5 and to_do[3] < 0.5:
                #     car.delta_y = 0
                # # Up Key
                # if to_do[2] > to_do[3]:
                #     car.delta_y = DELTA_X_LEFT_CONSTANT
                # # Down Key
                # elif to_do[3] > to_do[2]:
                #     car.delta_y = DELTA_X_RIGHT_CONSTANT
                car.shoot_rays(course)

            # See event detection loop - keyboard key down events
            car.turn_left_right()
            car.move_up_down()


            # Check for a collision event with the boundaries of the course
            if collision_with_course(car, course):
                collision_event_detected = True

        # Collision event detected
        else:
            # Display the game over message and wait before starting a new game
            if recorder:
                recorder.save()
            game_over(score)
            return score

        # Update the contents of the entire display
        pygame.display.update()
        if recorder:
            recorder.add_frame()
        clock.tick(60)

# Initialise the imported PyGame modules
pygame.init()

# Start the screen
screen = initialize_screen()

# Maintain the screen until the user closes the window
request_window_close = False

# Initialise a clock to track time
clock = pygame.time.Clock()

# Maintain the game loop until a collision event
collision_event_detected = False

if __name__ == "__main__":
    # Start the indefinite game loop
    indefinite_game_loop()
