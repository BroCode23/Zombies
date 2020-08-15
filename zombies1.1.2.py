from math import hypot
from random import randint, uniform
import pygame

# colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Size Variables
ZOMBIE_SIZE = 17
ZOMBIE_RADIUS = int(ZOMBIE_SIZE / 2)
SLOW_ZOMB = 2
FAST_ZOMB = 5
PLAYER_BOX = 28
PLAYER_CENTER = int(PLAYER_BOX / 2)
PLAYER_RADIUS = 10
PLAYER_SPEED = 5
BULLET_BOX = 4
BULLET_RADIUS = int(BULLET_BOX / 2)
SLOW_BULLET = 8
FAST_BULLET = 16
WINDOW_X = 500
WINDOW_Y = 500
PLAYER_START_X = 100
PLAYER_START_Y = 100
X_CHANGE = 0
Y_CHANGE = 0
MOUSEX = 0
MOUSEY = 0
SCORE = 0

# start the game engine
pygame.init()

# make the mouse look pretty
pygame.mouse.set_cursor(*pygame.cursors.diamond)

# define sprite groups
ENEMIES = pygame.sprite.Group()
GUN = pygame.sprite.Group()
BARRIERS = pygame.sprite.Group()


class PLAYER(pygame.sprite.Sprite):
    """player sprite that is controlled by the mouse and the arrow keys"""

    def __init__(self, x_loc, y_loc):
        super().__init__()
        # draw the PLAYER
        self.image = pygame.Surface((PLAYER_BOX, PLAYER_BOX), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE,
                           (PLAYER_CENTER, PLAYER_CENTER), PLAYER_RADIUS)

        self.rect = self.image.get_rect()
        self.radius = PLAYER_RADIUS
        self.rect.x = x_loc
        self.rect.y = y_loc

    def movement(self, d_x, d_y, unitx, unity):
        """Method used to move the player and detect barriers,
        d_x and d_y are the movement of the player, and
        unitx and unity are the unit vectors pointed towards the mouse position"""
        self.image.fill(pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE,
                           (PLAYER_CENTER, PLAYER_CENTER), PLAYER_RADIUS)
        pygame.draw.line(self.image, WHITE, [PLAYER_CENTER, PLAYER_CENTER], [
                         PLAYER_CENTER * unitx + PLAYER_CENTER, PLAYER_CENTER * unity + PLAYER_CENTER], PLAYER_RADIUS // 2)

        # detect BARRIERS on screen
        for barrier in pygame.sprite.spritecollide(PLAYER, BARRIERS, False):
            if PLAYER.rect.x < barrier.rect.x + barrier.image.get_width() and PLAYER.rect.x > barrier.rect.x + barrier.image.get_width() - PLAYER_SPEED - 1:
                #print("PLAYER right")
                PLAYER.rect.x += PLAYER_SPEED
            elif PLAYER.rect.x + PLAYER.image.get_width() > barrier.rect.x and PLAYER.rect.x + PLAYER.image.get_width() < barrier.rect.x + PLAYER_SPEED + 1:
                #print("PLAYER left")
                PLAYER.rect.x -= PLAYER_SPEED
            if PLAYER.rect.y < barrier.rect.y + barrier.image.get_height() and PLAYER.rect.y > barrier.rect.y + barrier.image.get_height() - PLAYER_SPEED - 1:
                #print("PLAYER bottom")
                PLAYER.rect.y += PLAYER_SPEED
            elif PLAYER.rect.y + PLAYER.image.get_height() > barrier.rect.y and PLAYER.rect.y + PLAYER.image.get_height() < barrier.rect.y + PLAYER_SPEED + 1:
                #print("PLAYER top")
                PLAYER.rect.y -= PLAYER_SPEED

        # detect the window borders and prevent from moving off screen
        if (self.rect.x < WINDOW_X - PLAYER_BOX and d_x > 0) or (d_x < 0 < self.rect.x):
            self.rect.x += d_x * PLAYER_SPEED
        if (self.rect.y < WINDOW_Y - PLAYER_BOX and d_y > 0) or (d_y < 0 < self.rect.y):
            self.rect.y += d_y * PLAYER_SPEED

    def shoot(self, unitx, unity):
        """player shoots a bullet towards the mouse location"""
        pellet = Bullet(self.rect.x + PLAYER_CENTER + (2 * PLAYER_RADIUS * unitx), self.rect.y +
                        PLAYER_CENTER + (2 * PLAYER_RADIUS * unity), unitx, unity, SLOW_BULLET)
        GUN.add(pellet)


class Zombie(pygame.sprite.Sprite):
    """Zombie sprite that follows the player and tries to eat them"""

    def __init__(self):
        super().__init__()
        # Draw the zombie
        self.image = pygame.Surface(
            (ZOMBIE_SIZE, ZOMBIE_SIZE),
            pygame.SRCALPHA
        )
        pygame.draw.circle(
            self.image,
            GREEN,
            [ZOMBIE_RADIUS, ZOMBIE_RADIUS],
            ZOMBIE_RADIUS
        )
        pygame.draw.ellipse(
            self.image, RED, [0, 0, ZOMBIE_SIZE, ZOMBIE_SIZE], 2)

        self.rect = self.image.get_rect()

        # set the spawn locaiton
        spawn_loc = randint(1, 4)
        if spawn_loc == 1:
            self.rect.x, self.rect.y = SPAWN1
        elif spawn_loc == 2:
            self.rect.x, self.rect.y = SPAWN2
        elif spawn_loc == 3:
            self.rect.x, self.rect.y = SPAWN3
        else:
            self.rect.x, self.rect.y = SPAWN4

        self.radius = ZOMBIE_RADIUS
        self.speed = uniform(SLOW_ZOMB, FAST_ZOMB)
        ENEMIES.add(self)

    def move_towards_player(self, playerx, playery):
        """Uses the players location to move in that direction avoiding barriers"""
        # find normalized direction vector (d_x, d_y) between enemy and PLAYER
        d_x, d_y = playerx - self.rect.x, playery - self.rect.y
        dist = hypot(d_x, d_y)
        d_x, d_y = d_x / dist, d_y / dist

        # detect BARRIERS
        collide = False
        for barrier in pygame.sprite.spritecollide(self, BARRIERS, False):
            collide = True
            if self.rect.x < barrier.rect.x + barrier.image.get_width() and self.rect.x > barrier.rect.x + barrier.image.get_width() - self.speed - 1:
                #print("zombie right")
                if d_x > 0:  # if moving away from the barrier
                    self.rect.x += d_x * self.speed
                    self.rect.y += d_y * self.speed
                else:  # moving laterally
                    if d_y > 0:
                        self.rect.y += self.speed
                    else:
                        self.rect.y -= self.speed
            elif self.rect.x + self.image.get_width() > barrier.rect.x and self.rect.x + self.image.get_width() < barrier.rect.x + self.speed + 1:
                #print("zombie left")
                if d_x < 0:  # if moving away from the barrier
                    self.rect.x += d_x * self.speed
                    self.rect.y += d_y * self.speed
                else:  # moving laterally
                    if d_y > 0:
                        self.rect.y += self.speed
                    else:
                        self.rect.y -= self.speed
            if self.rect.y < barrier.rect.y + barrier.image.get_height() and self.rect.y > barrier.rect.y + barrier.image.get_height() - self.speed - 1:
                #print("zombie bottom")
                if d_y > 0:  # if moving away from the barrier
                    self.rect.x += d_x * self.speed
                    self.rect.y += d_y * self.speed
                else:  # moving laterally
                    if d_x > 0:
                        self.rect.x += self.speed
                    else:
                        self.rect.x -= self.speed
            elif self.rect.y + self.image.get_height() > barrier.rect.y and self.rect.y + self.image.get_height() < barrier.rect.y + self.speed + 1:
                #print("zombie top")
                if d_y < 0:  # if moving away from the barrier
                    self.rect.x += d_x * self.speed
                    self.rect.y += d_y * self.speed
                else:  # moving laterally
                    if d_x > 0:
                        self.rect.x += self.speed
                    else:
                        self.rect.x -= self.speed

        # move along this normalized vector towards the PLAYER at current speed
        if not collide:
            self.rect.x += d_x * self.speed
            self.rect.y += d_y * self.speed


class Bullet(pygame.sprite.Sprite):
    """shot from the player, used to kill zombies"""

    # coordinates and direction of bullet and fast or slow bullet
    def __init__(self, x_loc, y_loc, unitvx, unitvy, speed):
        super().__init__()
        # draw the bullet
        self.image = pygame.Surface((BULLET_BOX, BULLET_BOX), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, [
                           BULLET_RADIUS, BULLET_RADIUS], BULLET_RADIUS)

        self.rect = self.image.get_rect()
        self.rect.x = x_loc
        self.rect.y = y_loc
        self.radius = BULLET_RADIUS
        self.speed = speed
        self.d_x = unitvx * self.speed
        self.d_y = unitvy * self.speed
        self.bounces = 0

    def calc_frame(self, score):
        """determines what the bullet should do each frame"""
        zombies_shot = pygame.sprite.spritecollide(self, ENEMIES, False)
        barrier_hit = pygame.sprite.spritecollide(self, BARRIERS, False)
        bullet_collision = pygame.sprite.spritecollide(self, GUN, False)
        # bullet out of bounds
        if self.rect.x > WINDOW_X or self.rect.y > WINDOW_Y or self.rect.x < 0 or self.rect.y < 0:
            GUN.remove(self)
        # check if zombies were shot
        elif zombies_shot:
            GUN.remove(self)
            ENEMIES.remove(zombies_shot[0])
            score += 50
        # check if bullet hit a barrier
        elif barrier_hit:
            self.bounce(barrier_hit[0])
        # check for bullet collision
        elif len(bullet_collision) > 1:
            GUN.remove(bullet_collision[1])
            GUN.remove(bullet_collision[0])
        else:
            self.zoom()
        return score

    def zoom(self):
        """method to control the movement of the bullet"""
        self.rect.x += self.d_x
        self.rect.y += self.d_y

    def bounce(self, wall):
        """method to calculate the bounce of a bullet off a wall"""
        # a bullet is only allowed one bounce, might change to multiple for a powerup
        if self.bounces > 0:
            GUN.remove(self)
            return
        self.bounces += 1

        if self.rect.x < wall.rect.x + wall.image.get_width() and self.rect.x > wall.rect.x + wall.image.get_width() - self.speed - 1:
            # print("right")
            self.d_x = self.d_x * -1
            self.rect.x += self.speed
        elif self.rect.x + self.image.get_width() > wall.rect.x and self.rect.x + self.image.get_width() < wall.rect.x + self.speed + 1:
            # print("left")
            self.d_x = self.d_x * -1
            self.rect.x -= self.speed
        if self.rect.y < wall.rect.y + wall.image.get_height() and self.rect.y > wall.rect.y + wall.image.get_height() - self.speed - 1:
            # print("bottom")
            self.d_y = self.d_y * -1
            self.rect.y += self.speed
        elif self.rect.y + self.image.get_height() > wall.rect.y and self.rect.y + self.image.get_height() < wall.rect.y + self.speed + 1:
            # print("top")
            self.d_y = self.d_y * -1
            self.rect.y -= self.speed


class Wall(pygame.sprite.Sprite):
    """Barrier sprite to restrict the movement of the other sprites"""

    def __init__(self, x_loc, y_loc, l, w):
        super().__init__()
        self.image = pygame.Surface((l, w))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x_loc
        self.rect.y = y_loc


# set up PLAYER sprite
PLAYER = PLAYER(PLAYER_START_X, PLAYER_START_Y)

# set up BARRIERS and zombie spawn locations for level 1
BARRIER1 = Wall(3, 3, 494, 50)
BARRIERS.add(BARRIER1)
BARRIER2 = Wall(3, 447, 494, 50)
BARRIERS.add(BARRIER2)
BARRIER3 = Wall(3, 100, 50, 300)
BARRIERS.add(BARRIER3)
BARRIER4 = Wall(447, 100, 50, 300)
BARRIERS.add(BARRIER4)
BARRIER5 = Wall(180, 225, 140, 50)
BARRIERS.add(BARRIER5)

SPAWN1 = (10, 58)
SPAWN2 = (475, 58)
SPAWN3 = (10, 425)
SPAWN4 = (475, 425)

# zombie spawn testing
"""ZOMB = Zombie(SPAWN1)
ENEMIES.add(ZOMB)
zomb2 = Zombie(SPAWN2)
ENEMIES.add(zomb2)
zomb3 = Zombie(SPAWN3)
ENEMIES.add(zomb3)
zomb4 = Zombie(SPAWN4)
ENEMIES.add(zomb4)"""

# Set the title of the window
pygame.display.set_caption('Zombies')
ROOM = pygame.display.set_mode([WINDOW_X, WINDOW_Y])

# its game time
DONE = False
CLOCK = pygame.time.Clock()
while not DONE:
    SHOT = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            DONE = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                X_CHANGE = -1
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                X_CHANGE = 1
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                Y_CHANGE = -1
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                Y_CHANGE = 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_w or event.key == pygame.K_s:
                Y_CHANGE = 0
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_a or event.key == pygame.K_d:
                X_CHANGE = 0
        if event.type == pygame.MOUSEBUTTONDOWN:
            SHOT = True

    # calculate the unit vector in components
    MOUSEX, MOUSEY = pygame.mouse.get_pos()
    VECTORX = MOUSEX - (PLAYER.rect.x + PLAYER_CENTER)
    VECTORY = MOUSEY - (PLAYER.rect.y + PLAYER_CENTER)
    MAG = hypot(VECTORX, VECTORY)
    UNIT_VX, UNIT_VY = float(VECTORX / MAG), float((VECTORY / MAG))

    # update player position
    PLAYER.movement(X_CHANGE, Y_CHANGE, UNIT_VX, UNIT_VY)

    # checks if more zombies should spawn
    if len(ENEMIES) < 10 and pygame.time.get_ticks() > 7000 and not pygame.time.get_ticks() % 15:
        Zombie()

    # zombie movement
    for zom in ENEMIES:
        # check if zombies ate the player
        if pygame.sprite.collide_circle(PLAYER, zom):
            print("zombie ate the player")
            DONE = True
            break
        zom.move_towards_player(
            PLAYER.rect.x + PLAYER_CENTER, PLAYER.rect.y + PLAYER_CENTER)

    # shooting mechanic
    if SHOT and len(GUN) < 5:
        PLAYER.shoot(UNIT_VX, UNIT_VY)

    # check what the bullet should do
    for bullet in GUN:
        # check if player was shot
        if pygame.sprite.collide_circle(PLAYER, bullet):
            print("player was shot")
            DONE = True
            break
        SCORE = bullet.calc_frame(SCORE)

    # setup score display
    SCORE_IMAGE = pygame.font.SysFont("arial", 30).render(
        "Score: %i" % SCORE, True, WHITE)

    # draw everything in the ROOM
    ROOM.fill(BLACK)
    GUN.draw(ROOM)
    ENEMIES.draw(ROOM)
    BARRIERS.draw(ROOM)
    ROOM.blit(PLAYER.image, (PLAYER.rect.x, PLAYER.rect.y))
    ROOM.blit(SCORE_IMAGE, [5, 0])
    pygame.display.flip()
    CLOCK.tick(20)
