import time
import pygame
import random
import sys
import mysql.connector
import hashlib

pygame.init()
# Nastavení připojení k databázi
DB_HOST = "dbs.spskladno.cz"
DB_USER = "student6"
DB_PASSWORD = "spsnet"
DB_NAME = "vyuka6"

def connect_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def save_score_to_db(name, difficulty, score):
    connection = connect_db()
    cursor = connection.cursor()

    # Získání ID hráče
    cursor.execute("SELECT id FROM 1hraci WHERE jmeno = %s", (name,))
    player_id = cursor.fetchone()
    if player_id is None:
        pass
    else:
        player_id = player_id[0]

    # Získání ID obtížnosti
    cursor.execute("SELECT id FROM 1obtiznosti WHERE difficulty_name = %s", (difficulty,))
    difficulty_id = cursor.fetchone()
    if difficulty_id is None:
        cursor.execute("INSERT INTO 1obtiznosti (difficulty_name) VALUES (%s)", (difficulty,))
        connection.commit()
        difficulty_id = cursor.lastrowid
    else:
        difficulty_id = difficulty_id[0]

    # Zkontroluj, zda už má hráč skóre pro tuto obtížnost
    cursor.execute("SELECT skore FROM 1skore WHERE player_id = %s AND difficulty_id = %s", (player_id, difficulty_id))
    existing_score = cursor.fetchone()

    if existing_score:
        # Pokud má hráč skóre a nové skóre je vyšší, přepíšeme ho
        if score > existing_score[0]:
            cursor.execute("UPDATE 1skore SET skore = %s WHERE player_id = %s AND difficulty_id = %s", (score, player_id, difficulty_id))
            print(f"Updated score for {name} to {score} in {difficulty}")
    else:
        # Pokud hráč ještě nemá skóre, vložíme nové skóre
        cursor.execute("INSERT INTO 1skore (player_id, difficulty_id, skore) VALUES (%s, %s, %s)", (player_id, difficulty_id, score))
        print(f"Inserted new score for {name}: {score} in {difficulty}")
    
    connection.commit()
    cursor.close()
    connection.close()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

FONT = pygame.font.Font(None, 36)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Obstacle Game")

clock = pygame.time.Clock()

HIGH_SCORE_FILE_ez = "osobní rekordy - easy.txt"
HIGH_SCORE_FILE_med = "osobní rekordy - medium.txt"
HIGH_SCORE_FILE_ha = "osobní rekordy - hard.txt"

def save_high_score_ez(player_name, score):
    try:
        # Načtení aktuálních skóre
        with open(HIGH_SCORE_FILE_ez, "r") as file:
            high_scores = file.readlines()

        
        high_scores.append(f"{player_name}: {score}\n")  # Přidej nového hráče

        # Seřaď skóre podle hodnoty (z nejvyššího)
        high_scores.sort(key=lambda x: float(x.split(": ")[1]), reverse=True)
        
        # Udržuj pouze top 10 skóre
        high_scores = high_scores[:10]

        # Ulož výsledky
        with open(HIGH_SCORE_FILE_ez, "w") as file:
            file.writelines(high_scores)
    except FileNotFoundError:
        # Pokud soubor neexistuje, vytvoř ho
        with open(HIGH_SCORE_FILE_ez, "w") as file:
            file.write(f"{player_name}: {score}\n")

def save_high_score_med(player_name, score):
    try:
        # Načtení aktuálních skóre
        with open(HIGH_SCORE_FILE_med, "r") as file:
            high_scores = file.readlines()

        
        high_scores.append(f"{player_name}: {score}\n")  # Přidej nového hráče

        # Seřaď skóre podle hodnoty (z nejvyššího)
        high_scores.sort(key=lambda x: float(x.split(": ")[1]), reverse=True)
        
        # Udržuj pouze top 10 skóre
        high_scores = high_scores[:10]

        # Ulož výsledky
        with open(HIGH_SCORE_FILE_med, "w") as file:
            file.writelines(high_scores)
    except FileNotFoundError:
        # Pokud soubor neexistuje, vytvoř ho
        with open(HIGH_SCORE_FILE_med, "w") as file:
            file.write(f"{player_name}: {score}\n")

def save_high_score_ha(player_name, score):
    try:
        # Načtení aktuálních skóre
        with open(HIGH_SCORE_FILE_ha, "r") as file:
            high_scores = file.readlines()

        
        high_scores.append(f"{player_name}: {score}\n")  # Přidej nového hráče

        # Seřaď skóre podle hodnoty (z nejvyššího)
        high_scores.sort(key=lambda x: float(x.split(": ")[1]), reverse=True)
        
        # Udržuj pouze top 10 skóre
        high_scores = high_scores[:10]

        # Ulož výsledky
        with open(HIGH_SCORE_FILE_ha, "w") as file:
            file.writelines(high_scores)
    except FileNotFoundError:
        # Pokud soubor neexistuje, vytvoř ho
        with open(HIGH_SCORE_FILE_ha, "w") as file:
            file.write(f"{player_name}: {score}\n")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
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
        self.difficulty_increment_timer = 0  # Nový časovač na zvýšení obtížnosti

    def update(self):
        self.spawn_timer += 1
        self.difficulty_increment_timer += 1  # Sleduj čas od posledního zvýšení obtížnosti

        if self.spawn_timer >= self.spawn_interval:
            self.spawn_obstacle()
            self.spawn_timer = 0

        if self.difficulty_increment_timer >= 300:  # Každých 300 snímků zvýší obtížnost
            self.increase_difficulty()
            self.difficulty_increment_timer = 0

        self.obstacles.update()

    def increase_difficulty(self):
        # Zrychlí překážky a zvýší frekvenci jejich spawnování
        self.obstacle_speed += 0.2
        if self.spawn_interval > 20:  # Ujisti se, že interval neklesne pod minimální hodnotu
            self.spawn_interval -= 2

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

        new_obstacle = Obstacle(x, y, 50, 50, speed_x, speed_y)
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
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if respawn_rect.collidepoint(mouse_pos):
                    return True

def register_player():
    screen.fill((0, 0, 0))
    name_text = FONT.render("Zadejte jméno: ", True, WHITE)
    screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    pygame.display.flip()
    
    name = get_player_name()

    # Kontrola, zda jméno již existuje
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM 1hraci WHERE jmeno = %s", (name,))
    if cursor.fetchone() :
        # Pokud jméno existuje, informuj uživatele a vrať ho zpět na registraci
        error_text = FONT.render("Toto jméno je už zaregistrované.", True, RED)
        screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()
        time.sleep(2)
        return register_player()
    elif name == '' :
        error_text = FONT.render("Není možné.", True, RED)
        screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()
        time.sleep(2)
        return register_player()

    # Zadání a kontrola hesla
    password = get_password("Zadejte heslo: ")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hashe hesla

    # Uložení hráče do databáze
    cursor.execute("INSERT INTO 1hraci (jmeno, heslo) VALUES (%s, %s)", (name, hashed_password))
    connection.commit()
    cursor.close()
    connection.close()

    print(f"Player {name} registered successfully.")
    return name

def get_password(prompt):
    input_active = True
    password = ''
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    password = password[:-1]
                else:
                    password += event.unicode
        screen.fill((0, 0, 0))
        password_text = FONT.render(f"{prompt} {password}", True, WHITE)
        screen.blit(password_text, (SCREEN_WIDTH // 2 - password_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
    if password =='' :
        error_text = FONT.render("Musíme zadat heslo.", True, RED)
        screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()
        time.sleep(2)
        return get_password("Zadejte heslo:")
    return password

def login_player():
    screen.fill((0, 0, 0))
    name_text = FONT.render("Zadejte jméno: ", True, WHITE)
    screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    pygame.display.flip()

    name = get_player_name()

    # Zadání hesla
    password = get_password("Zadejte heslo: ")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hashe hesla

    # Kontrola přihlášení
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM 1hraci WHERE jmeno = %s AND heslo = %s", (name, hashed_password))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        print(f"Player {name} logged in successfully.")
        return name
    else:
        # Pokud přihlášení selže
        error_text = FONT.render("Špatné heslo nebo jméno.", True, RED)
        screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()
        time.sleep(2)
        return login_player()
        
    

def get_player_name():
    input_active = True
    name = ''
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
        screen.fill((0, 0, 0))
        name_text = FONT.render(f"Enter your name: {name}", True, WHITE)
        screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
    return name

def main_menu():
    screen.fill((0, 0, 0))
    register_text = FONT.render("Register", True, GREEN)
    login_text = FONT.render("Login", True, BLUE)
    register_rect = register_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    login_rect = login_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(register_text, register_rect)
    screen.blit(login_text, login_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if register_rect.collidepoint(mouse_pos):
                    return "register"
                elif login_rect.collidepoint(mouse_pos):
                    return "login"

def difficulty_selection():
    screen.fill((0, 0, 0))
    easy_text = FONT.render("Lehká", True, GREEN)
    medium_text = FONT.render("Střední", True, BLUE)
    hard_text = FONT.render("Těžká", True, RED)
    easy_rect = easy_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    medium_rect = medium_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    hard_rect = hard_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(easy_text, easy_rect)
    screen.blit(medium_text, medium_rect)
    screen.blit(hard_text, hard_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if easy_rect.collidepoint(mouse_pos):
                    return 'easy'
                elif medium_rect.collidepoint(mouse_pos):
                    return 'medium'
                elif hard_rect.collidepoint(mouse_pos):
                    return 'hard'
# Hlavní herní smyčka
all_sprites = pygame.sprite.Group()
obstacle_manager = ObstacleManager()
player = Player()
all_sprites.add(player)

choice = main_menu()
if choice == "register":
    player_name = register_player()
elif choice == "login":
    player_name = login_player()

start_time = pygame.time.get_ticks()
while True:
    
    difficulty = difficulty_selection()

    if difficulty == 'easy':
        obstacle_manager.spawn_interval = 100
        obstacle_manager.obstacle_speed = 4
    elif difficulty == 'medium':
        obstacle_manager.spawn_interval = 50
        obstacle_manager.obstacle_speed = 5
    elif difficulty == 'hard':
        obstacle_manager.spawn_interval = 30
        obstacle_manager.obstacle_speed = 6

    obstacle_manager.difficulty_increment_timer = 0  # Reset časovače obtížnosti


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
                sys.exit()

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
            if difficulty == 'easy':
                save_high_score_ez(player_name,time_alive/1000)

            elif difficulty == 'medium':
                save_high_score_med(player_name, float(time_alive/1000))

            elif difficulty == 'hard':
                save_high_score_ha(player_name, float(time_alive/1000))

            save_score_to_db(player_name, difficulty, float(time_alive/1000))

            if game_over_screen(time_alive):
                break
            
            high_score_text = FONT.render("Přežil jsi: {} sekund".format(time_alive // 1000), True, WHITE)
            screen.blit(high_score_text, (10, 40))

pygame.quit()
sys.exit()

#1hraci	CREATE TABLE `1hraci` (
# `id` int(11) NOT NULL AUTO_INCREMENT,
# `jmeno` text DEFAULT NULL,
#`heslo` text DEFAULT NULL,
#`is_admin` tinyint(1) DEFAULT NULL,
# PRIMARY KEY (`id`),
# UNIQUE KEY `jmeno` (`jmeno`) USING HASH
#) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci
#1obtiznosti	CREATE TABLE `1obtiznosti` (
# `id` int(11) NOT NULL AUTO_INCREMENT,
# `difficulty_name` text DEFAULT NULL,
# PRIMARY KEY (`id`),
# UNIQUE KEY `difficulty_name` (`difficulty_name`) USING HASH
#) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci
#1skore	CREATE TABLE `1skore` (
# `player_id` int(11) NOT NULL,
# `difficulty_id` int(11) NOT NULL,
# `skore` float DEFAULT NULL,
# PRIMARY KEY (`player_id`,`difficulty_id`),
# KEY `difficulty_id` (`difficulty_id`),
# CONSTRAINT `1skore_ibfk_1` FOREIGN KEY (`player_id`) REFERENCES `1hraci` (`id`),
# CONSTRAINT `1skore_ibfk_2` FOREIGN KEY (`difficulty_id`) REFERENCES `1obtiznosti` (`id`)
#) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci