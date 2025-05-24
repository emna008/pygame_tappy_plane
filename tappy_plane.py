import pygame
from pygame.locals import *
import random
import os

pygame.init()
pygame.mixer.init()

game_width, game_height = 800, 480
window_size = (game_width, game_height)
game_window = pygame.display.set_mode(window_size)
pygame.display.set_caption('Tappy Plane')

font = pygame.font.SysFont('Arial', 30)

# Fonction pour redimensionner les images
def scale_image(image, new_width):
    scale = new_width / image.get_rect().width
    new_height = image.get_rect().height * scale
    return pygame.transform.scale(image, (int(new_width), int(new_height)))

# Chargement des images
def load_images():
    images = {
        'bg': pygame.image.load('images/background.png').convert_alpha(),
        'ground': scale_image(pygame.image.load('images/groundGrass.png').convert_alpha(), 400),
        'rock_up': pygame.image.load('images/rockGrass.png').convert_alpha(),
        'rock_down': pygame.image.load('images/rockGrassDown.png').convert_alpha(),
        'star': scale_image(pygame.image.load('images/starGold.png').convert_alpha(), 20),
        'heart': scale_image(pygame.image.load('images/heart.png').convert_alpha(), 30),
        'start': pygame.image.load('images/start.png').convert_alpha(),
        'gameover': pygame.image.load('images/textGameOver.png').convert_alpha(),
        'numbers': [pygame.image.load(f'images/number{i}.png').convert_alpha() for i in range(10)],
        'planes': [scale_image(pygame.image.load(f'images/planeRed{i}.png').convert_alpha(), 50) for i in range(1, 4)]
    }
    return images

# Chargement des sons
def load_sounds():
    sounds = {
        'jump': pygame.mixer.Sound('sounds/jump.wav'),
        'collect': pygame.mixer.Sound('sounds/collect.wav'),
        'crash': pygame.mixer.Sound('sounds/crash.wav'),
    }
    pygame.mixer.music.load('sounds/background_music.mp3')
    pygame.mixer.music.set_volume(0.5)
    return sounds

# Écran de démarrage
def show_start_screen():
    game_window.blit(images['bg'], (0, 0))
    game_window.blit(images['start'], (game_width // 2 - images['start'].get_width() // 2, 
                                      game_height // 2 - images['start'].get_height() // 2))
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                waiting = False
    return True

# Affichage du score
def display_score(score):
    num_digits = len(str(score))
    score_x = game_width // 2 - images['numbers'][0].get_width() * num_digits // 2
    for digit in str(score):
        game_window.blit(images['numbers'][int(digit)], (score_x, 30))
        score_x += images['numbers'][int(digit)].get_width()
# Affichage des vies
def display_lives(lives):
    lives_x = 10
    for _ in range(lives):
        game_window.blit(images['heart'], (lives_x, 10))
        lives_x += images['heart'].get_width() + 5

# Classes des éléments du jeu
class Ground(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = images['ground']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = game_height - self.image.get_height()

    def update(self):
        self.rect.x -= 2
        if self.rect.right <= 0:
            self.rect.x = game_width

class Rock(pygame.sprite.Sprite):
    def __init__(self, x, direction):
        super().__init__()
        self.image = images['rock_up'] if direction == 'up' else images['rock_down']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = game_height - self.image.get_height() if direction == 'up' else 0
        self.direction = direction

    def update(self):
        self.rect.x -= 2
        if self.rect.right <= 0:
            self.kill()
            new_x = max(r.rect.x for r in rock_group) + random.randint(200, 400)
            rock_group.add(Rock(new_x, self.direction))
            star_x = new_x + random.randint(-100, 100)
            star_y = (game_height - images['rock_up'].get_height() - random.randint(50, 100)) if self.direction == 'up' else (images['rock_down'].get_height() + random.randint(50, 100))
            star_group.add(Star(star_x, star_y))

class Plane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_index = 0
        self.image = images['planes'][self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = 80
        self.rect.y = game_height // 2
        self.score = 0
        self.lives = 3
        self.gravity = 0.6  
        self.lift = -10    
        self.velocity = 0
        self.max_speed = 8

    def update(self):
        self.velocity += self.gravity
        self.velocity = min(self.velocity, 10)  
        self.rect.y += self.velocity
        
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0
        if self.rect.bottom > game_height:
            self.rect.bottom = game_height
            self.velocity = 0
        
        self.image_index = (self.image_index + 0.3) % len(images['planes'])
        self.image = images['planes'][int(self.image_index)]
    def fly_up(self):
        self.velocity = self.lift  
        sounds['jump'].play()
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = images['star']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x -= 2
        if self.rect.right <= 0:
            self.kill()

images = load_images()
sounds = load_sounds()
pygame.mixer.music.play(-1)  

ground_group = pygame.sprite.Group()
rock_group = pygame.sprite.Group()
star_group = pygame.sprite.Group()
plane_group = pygame.sprite.Group()

# Création du sol
for x in range(0, game_width + 1, images['ground'].get_width()):
    ground_group.add(Ground(x))

# Création des rochers et étoiles
direction = 'up'
last_x = game_width
for _ in range(4):
    rock_group.add(Rock(last_x, direction))
    star_x = last_x + random.randint(-100, 100)
    star_y = (game_height - images['rock_up'].get_height() - random.randint(50, 100)) \
              if direction == 'up' else \
             (images['rock_down'].get_height() + random.randint(50, 100))
    star_group.add(Star(star_x, star_y))
    last_x += random.randint(200, 400)
    direction = 'down' if direction == 'up' else 'up'

# Création de l'avion
plane = Plane()
plane_group.add(plane)

# Initialisation du défilement du fond
bg_scroll = 0

# Boucle principale
clock = pygame.time.Clock()
fps = 60  
running = True
gameover = False

if not show_start_screen():
    running = False
    
bg_scroll_speed = 3

while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN or (event.type == KEYDOWN and event.key == K_SPACE):
            plane.fly_up()
    # Défilement du fond
    game_window.blit(images['bg'], (0 - bg_scroll, 0))
    game_window.blit(images['bg'], (game_width - bg_scroll, 0))
    bg_scroll += bg_scroll_speed
    if bg_scroll >= game_width:
        bg_scroll = 0

    # Mise à jour des éléments
    ground_group.update()
    rock_group.update()
    star_group.update()
    plane_group.update()

    # Affichage
    ground_group.draw(game_window)
    rock_group.draw(game_window)
    star_group.draw(game_window)
    plane_group.draw(game_window)

    # Collision avec les étoiles
    if pygame.sprite.spritecollide(plane, star_group, True, pygame.sprite.collide_mask):
        plane.score += 1
        sounds['collect'].play()

    # Collision avec les obstacles
    if (pygame.sprite.spritecollide(plane, rock_group, False, pygame.sprite.collide_mask) or 
        pygame.sprite.spritecollide(plane, ground_group, False, pygame.sprite.collide_mask)):
        plane.lives -= 1
        sounds['crash'].play()
        if plane.lives <= 0:
            gameover = True
        else:
            plane.rect.y = game_height // 2  

    display_score(plane.score)
    display_lives(plane.lives)

    # Game Over
    while gameover:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                gameover = False

        game_window.blit(images['gameover'], 
                        (game_width // 2 - images['gameover'].get_width() // 2, 
                         game_height // 2 - images['gameover'].get_height() // 2))
        score_text = font.render(f"Score: {plane.score}", True, (0, 0, 0))
        game_window.blit(score_text, (game_width // 2 - score_text.get_width() // 2, 
                                    game_height // 2 + 50))

    pygame.display.update()

pygame.quit()