#!/usr/bin/env python3
"""Car racing game written in Python.

This module implements a simple car driving game in Python using object
oriented programming principles and the Pygame engine. The aim of the game is
to overtake other cars without colliding with them. If you do collide with
either the other cars or the screen boundary, then it is game over.

Attribution:
    Splash Screen Image:
        <a href='https://www.freepik.com/vectors/background'>
            Background vector created by macrovector - www.freepik.com
        </a>
    Human Player Car Image:
        <a href="https://www.freepik.com/vectors/car">
            Car vector created by freepik - www.freepik.com
        </a>
    Computer Player Car Image:
        https://pixabay.com/vectors/car-racing-speed-auto-green-312571/

"""

import math
import pygame
import random
import time

import numpy as np

from course import generate_course
from nn import move_car

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
OVERTAKE_COMPUTER_SCORE_INCREMENT = 10

# Colors
BLACK = (0, 0, 0)
GREY = (211, 211, 211)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


class Car:

    def __init__(self, pos_x=0, pos_y=0, delta_x=DELTA_X_RIGHT_CONSTANT,
                 delta_y=0, theta=90, delta_theta=0, human=False):
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
        self.human = human
        self.image = None
        self.bounding_box = None
        self.aa_bounding_box = None
        self.rays = np.zeros(5)
        self.current_box = 0

    def load_transform_image(self):
        """Load the car image from the filesystem."""

        self.image = pygame.image.load(
            HUMAN_PLAYER_IMAGE_FILENAME).convert() if self.human else \
            pygame.image.load(COMPUTER_PLAYER_IMAGE_FILENAME).convert()
        self.image.set_colorkey(BLACK)
        self.image = pygame.transform.scale(
            self.image, HUMAN_PLAYER_IMAGE_SIZE) if self.human else \
            pygame.transform.scale(self.image, COMPUTER_PLAYER_IMAGE_SIZE)

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
        self.pos_x += self.delta_y * math.sin(self.theta / 180 * math.pi)
        self.pos_y += self.delta_y * math.cos(self.theta / 180 * math.pi)

    def check_score_accumulated(self):
        score = 0

        current = course.path[self.current_box]
        pygame.draw.rect(screen, GREEN, [current[0]*BOX_SIZE, current[1]*BOX_SIZE, BOX_SIZE, BOX_SIZE])

        if pygame.Rect(current[0]*BOX_SIZE, current[1]*BOX_SIZE, BOX_SIZE, BOX_SIZE).collidepoint(self.pos_x, self.pos_y):
            self.current_box += 1
            score += 1
        return score
    def shoot_rays(self):

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
                self.rays[i] = -1
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

    tolerance = 10

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

        # def render_course(self):
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
        delta_y=0,
        human=True)

    # Transform and scale the size of the player car image to fit the screen
    human_player_car.load_transform_image()

    return human_player_car


def create_computer_players():
    """Create a list of car objects that act as obstacles."""

    # Create computer car object obstacles
    for n in range(COMPUTER_PLAYER_COUNT):
        # Randomly initialise the initial (x, y) co-ordinate for this computer
        init_x = random.randrange(
            0, SCREEN_SIZE[0] - COMPUTER_PLAYER_IMAGE_SIZE[0])
        init_y = random.randrange(-125, -25)

        # Randomise the rate of change in the y-plane, starting with slow speeds
        init_delta_y = random.randint(2, 3)

        # Create a new computer player
        global computer_players
        computer_player_car = Car(
            pos_x=init_x,
            pos_y=init_y,
            delta_x=0,
            delta_y=init_delta_y,
            human=False)

        # Transform and scale the size of the computer player car image
        computer_player_car.load_transform_image()

        # Add the new computer player to the list of computer players
        computer_players.append(computer_player_car)


def collision_with_course():
    """Check whether the human car object has exceeded the screen boundaries
    along the x-plane."""

    for line in course.lines:
        if human_player.bounding_box.clipline(line):
            return True
    return False


def collision_with_screen_boundaries():
    """Check whether the human car object has exceeded the screen boundaries
    along the x-plane."""

    # Check whether the position of the player exceeds the screen boundaries
    if human_player.pos_x > SCREEN_SIZE[0] - HUMAN_PLAYER_IMAGE_SIZE[0] or \
            human_player.pos_x < 0:
        return True
    return False


def collision_with_computer():
    """Check whether the human car object has collided with one of the
    computer car objects."""

    # Check whether the player has collided with a computer player
    for n in range(COMPUTER_PLAYER_COUNT):

        # Get the current (x, y) position of the current computer player
        computer_pos_x = computer_players[n].pos_x
        computer_pos_y = computer_players[n].pos_y

        if (human_player.pos_x + HUMAN_PLAYER_IMAGE_SIZE[0] > computer_pos_x) \
                and (human_player.pos_x < computer_pos_x +
                     COMPUTER_PLAYER_IMAGE_SIZE[0]) \
                and (human_player.pos_y < computer_pos_y +
                     COMPUTER_PLAYER_IMAGE_SIZE[1]) \
                and (human_player.pos_y +
                     HUMAN_PLAYER_IMAGE_SIZE[1] > computer_pos_y):
            return True

    return False


def game_over(score):
    """If a collision event has occurred, render a game over message, then reset
    the game parameters before starting a new indefinite game loop after
    a brief pause."""

    # Display the game over message along with the score
    global speed_increment
    font = pygame.font.Font(MESSAGE_FONT, MESSAGE_FONT_SIZE)
    text = font.render(MESSAGE_GAME_OVER + str(score), True, BLACK)
    text_rectangle = text.get_rect()
    text_rectangle.center = ((SCREEN_SIZE[0] / 2), (SCREEN_SIZE[1] / 2))
    screen.blit(text, text_rectangle)
    pygame.display.update()

    # Pause the application before continuing with a new game loop
    time.sleep(2)

    # Reset the game parameters
    global clock, human_player, computer_players, collision_event_detected
    clock = pygame.time.Clock()
    human_player = create_human_player()
    computer_players = []
    create_computer_players()
    collision_event_detected = False
    speed_increment = 2

    # # Start a new game via the indefinite game loop
    # indefinite_game_loop()


def indefinite_game_loop(nn=None):
    """Vector racing game events and subsequent display rendering actions."""
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
                    human_player.delta_theta = 5

                # Right Key
                if event.key == pygame.K_RIGHT:
                    human_player.delta_theta = -5

                # up Key
                if event.key == pygame.K_UP:
                    human_player.delta_y += DELTA_X_LEFT_CONSTANT

                # down Key
                if event.key == pygame.K_DOWN:
                    human_player.delta_y += DELTA_X_RIGHT_CONSTANT

            # Keyboard Key Up Event
            if event.type == pygame.KEYUP:

                # Left or Right Key
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    human_player.delta_theta = 0

                # Up or Down Key
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    human_player.delta_y = 0

        # ----- UPDATE DISPLAY -----

        # Fill the display with a white background
        screen.fill(GREY)

        #check score
        score += human_player.check_score_accumulated()


        # Whilst there is no collision event
        global collision_event_detected

        if not collision_event_detected and (time.time() - start) < 5:

            course.render_course()

            # Render the player car object
            human_player.render_image()

            # Ask AI what to do
            if nn:
                to_do = nn.activate(human_player.rays)

                if to_do[0] < 0.5 and to_do[1] < 0.5:
                    human_player.delta_theta = 0
                # Left Key
                if to_do[0] > to_do[1]:
                    human_player.delta_theta = 5
                # Right Key
                elif to_do[1] > to_do[0]:
                    human_player.delta_theta = -5

                if to_do[2] < 0.5 and to_do[3] < 0.5:
                    human_player.delta_y = 0
                # Up Key
                if to_do[2] > to_do[3]:
                    human_player.delta_y = DELTA_X_LEFT_CONSTANT
                # Down Key
                elif to_do[3] > to_do[2]:
                    human_player.delta_y = DELTA_X_RIGHT_CONSTANT

            # See event detection loop - keyboard key down events
            human_player.turn_left_right()
            human_player.move_up_down()
            human_player.shoot_rays()

            # Check for a collision event with the screen boundaries
            if collision_with_screen_boundaries():
                collision_event_detected = True

            # Check for a collision event with the boundaries of the course
            if collision_with_course():
                collision_event_detected = True

            # Check for a collision event with a computer player
            if collision_with_computer():
                collision_event_detected = True

        # Collision event detected
        else:

            # Display the game over message and wait before starting a new game
            game_over(score)
            return score

        # Update the contents of the entire display
        pygame.display.update()
        clock.tick(60)

# Initialise the imported PyGame modules
pygame.init()

# Start the screen
screen = initialize_screen()

# Maintain the screen until the user closes the window
request_window_close = False

# Initialise a clock to track time
clock = pygame.time.Clock()

# Create Course
course = Course()

# Create the human player
human_player = create_human_player()

# Maintain the game loop until a collision event
collision_event_detected = False

# Keep score
score = 0

# Maintain a game speed incrementer
speed_increment = 2

if __name__ == "__main__":
    # Start the indefinite game loop
    indefinite_game_loop()
