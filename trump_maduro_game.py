import pygame
import random
import os

# =========================================================
# CLASE Player (Donald Trump)
# =========================================================
class Player:
    def __init__(self, x, y, size, speed, image_path):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed
        try:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (size, size))
        except pygame.error:
            # Si no encuentra la imagen, crea un rectángulo de color
            self.image = pygame.Surface((size, size))
            self.image.fill((0, 150, 255))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def keep_inside_screen(self, width, height):
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(height - self.rect.height, self.rect.y))

    def update(self, screen_width, screen_height):
        self.handle_input()
        self.keep_inside_screen(screen_width, screen_height)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# =========================================================
# CLASE Enemy (Maduro)
# =========================================================
class Enemy:
    def __init__(self, radius, screen_width, screen_height, image_path):
        self.radius = radius
        self.screen_width = screen_width
        self.screen_height = screen_height
        try:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (radius * 2, radius * 2))
        except pygame.error:
            # Si no encuentra la imagen, crea un círculo de color
            self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 0), (radius, radius), radius)
        self.respawn()

    def respawn(self):
        self.x = random.randint(self.radius, self.screen_width - self.radius)
        self.y = random.randint(self.radius, self.screen_height - self.radius)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def draw(self, screen):
        screen.blit(self.image, (self.x - self.radius, self.y - self.radius))


# =========================================================
# CLASE Score
# =========================================================
class Score:
    def __init__(self, font):
        self.points = 0
        self.font = font

    def add(self, amount=1):
        self.points += amount

    def reset(self):
        self.points = 0

    def draw(self, screen):
        text_surface = self.font.render(f"Puntuación: {self.points}", True, (255, 255, 255))
        # Crear un rectángulo negro detrás del texto
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, 10)
        # Añadir padding al rectángulo
        bg_rect = text_rect.inflate(20, 20)
        bg_rect.topleft = (5, 5)
        # Dibujar fondo negro y luego el texto
        pygame.draw.rect(screen, (0, 0, 0), bg_rect)
        screen.blit(text_surface, text_rect)


# =========================================================
# CLASE SoundManager
# =========================================================
class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self.background_music = None

        try:
            pygame.mixer.init()
        except pygame.error:
            self.enabled = False

    def load_sound(self, name, filepath):
        if not self.enabled or not os.path.exists(filepath):
            return
        try:
            self.sounds[name] = pygame.mixer.Sound(filepath)
        except pygame.error:
            pass

    def load_music(self, filepath):
        if not self.enabled or not os.path.exists(filepath):
            return
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play(-1)  # -1 = reproducción infinita
        except pygame.error:
            pass

    def play(self, name):
        if not self.enabled:
            return
        if name in self.sounds:
            self.sounds[name].play()


# =========================================================
# CLASE Game
# =========================================================
class Game:
    def __init__(self):
        # Configuración
        self.width = 1000
        self.height = 800
        self.fps = 60

        # Inicialización Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Jaime Verdugo Serrano") 
        self.clock = pygame.time.Clock()

        # Recursos
        self.font = pygame.font.SysFont(None, 48)
        self.sound_manager = SoundManager()

        # Cargar imagen de fondo (Venezuela)
        self.background = None
        self.load_background()

        # Cargar sonidos
        # - capture_sound.wav (sonido cuando captures a Maduro)
        # - background_music.mp3 (música de fondo)
        self.sound_manager.load_music("assets/background_music.mp3")
        self.sound_manager.load_sound("capture", "assets/capture_sound.wav")

        # Objetos del juego
        # - trump.png (cara de Donald Trump)
        # - maduro.png (cara de Maduro)
        self.player = Player(
            x=self.width // 2,
            y=self.height // 2,
            size=120,
            speed=6,
            image_path="assets/trump.png"
        )
        self.enemy = Enemy(
            radius=80,
            screen_width=self.width,
            screen_height=self.height,
            image_path="assets/maduro.png"
        )
        self.score = Score(font=self.font)

        # Estado
        self.running = True

    def load_background(self):
        """Carga la imagen de fondo de Venezuela"""
        try:
            self.background = pygame.image.load("assets/venezuela_map.png")
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except pygame.error:
            # Si no existe, crea un fondo de color
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill((34, 139, 34))  # Verde oscuro

    def handle_events(self):
        try:
            events = pygame.event.get()
        except Exception as e:
            print("Error en pygame.event.get():", repr(e))
            # Intento de recuperación: limpiar cola de eventos y seguir
            try:
                pygame.event.clear()
            except Exception:
                pass
            return

        for event in events:
            # Mostrar información útil para diagnóstico (puedes quitarlo luego)
            # print("Evento:", event, "type:", getattr(event, 'type', None))
            if event.type == pygame.QUIT:
                self.running = False

    def check_collision(self):
        """Detecta colisión entre Trump y Maduro"""
        if self.player.rect.colliderect(self.enemy.get_rect()):
            self.score.add(1)
            self.enemy.respawn()
            self.sound_manager.play("capture")

    def update(self):
        self.player.update(self.width, self.height)
        self.check_collision()

    def draw(self):
        # Dibujar fondo
        self.screen.blit(self.background, (0, 0))

        # Dibujar objetos
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        self.score.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)

        pygame.quit()


# =========================================================
# PUNTO DE ENTRADA
# =========================================================
if __name__ == "__main__":
    game = Game()
    game.run()