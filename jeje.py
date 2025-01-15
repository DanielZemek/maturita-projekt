import pygame
import random


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

FONT = pygame.font.Font(None, 36)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Obstacle Game")

clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([1, 1])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = SCREEN_HEIGHT // 2 
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        self.rect.x = max(0, min(SCREEN_WIDTH - 50, self.rect.x))
        self.rect.y = max(0, min(SCREEN_HEIGHT - 50, self.rect.y))

class ObstacleManager(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.obstacles = pygame.sprite.Group()
        self.spawn_timer = 0
        self.spawn_interval = 120 
        self.obstacle_speed = 5

    def update(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_obstacle()
            self.spawn_timer = 0

        self.obstacles.update()

    def draw(self, screen):
        self.obstacles.draw(screen)

    def spawn_obstacle(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, SCREEN_WIDTH - 50)
            y = -50
            speed_x = 0
            speed_y = self.obstacle_speed
        elif side == 'bottom':
            x = random.randint(0, SCREEN_WIDTH - 50)
            y = SCREEN_HEIGHT
            speed_x = 0
            speed_y = -self.obstacle_speed
        elif side == 'left':
            x = -50
            y = random.randint(0, SCREEN_HEIGHT - 50)
            speed_x = self.obstacle_speed
            speed_y = 0
        else:  
            x = SCREEN_WIDTH
            y = random.randint(0, SCREEN_HEIGHT - 50)
            speed_x = -self.obstacle_speed
            speed_y = 0

        new_obstacle = Obstacle(x, y, 25, 25, speed_x, speed_y)
        self.obstacles.add(new_obstacle)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, speed_x, speed_y):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.x > SCREEN_WIDTH or self.rect.x < -self.rect.width \
                or self.rect.y > SCREEN_HEIGHT or self.rect.y < -self.rect.height:
            self.kill()

def game_over_screen(time_alive):
    screen.fill((0, 0, 0))
    text = FONT.render("Game Over! You survived for {} seconds.".format(time_alive // 1000), True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)

    respawn_text = FONT.render("Respawn", True, GREEN)
    respawn_rect = respawn_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.draw.rect(screen, GREEN, respawn_rect, 2)
    screen.blit(respawn_text, respawn_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if respawn_rect.collidepoint(mouse_pos):
                    return True


    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
            

all_sprites = pygame.sprite.Group()
obstacle_manager = ObstacleManager()
player = Player()
all_sprites.add(player)

start_time = pygame.time.get_ticks()
while True:
    obstacle_manager.spawn_interval = 1
    obstacle_manager.obstacle_speed = 1

    game_over = False
    player.rect.centerx = SCREEN_WIDTH // 2 
    player.rect.centery = SCREEN_HEIGHT // 2
    all_sprites.empty()
    obstacle_manager.obstacles.empty()
    all_sprites.add(player)
    start_time = pygame.time.get_ticks() 

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                

        if not game_over:
            hits = pygame.sprite.spritecollide(player, obstacle_manager.obstacles, False)
            if hits:
                game_over = True

            all_sprites.update()
            obstacle_manager.update()

            screen.fill((0, 0, 0))
            all_sprites.draw(screen)
            obstacle_manager.draw(screen)

            time_alive = pygame.time.get_ticks() - start_time
            time_text = FONT.render("Time: {} seconds".format(time_alive // 1000), True, WHITE)
            screen.blit(time_text, (10, 10))
            pygame.display.flip()
            clock.tick(60)

        if game_over:
            if game_over_screen(time_alive):
                break

pygame.quit()
