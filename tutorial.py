import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 650
FPS = 60
PLAYER_VEL = 5
skin = "MaskDude"
skin_2 = "MaskDude"

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    """
    Отражает список спрайтов по горизонтали.

    :param sprites: Список спрайтов, которые необходимо отразить.
    :type sprites: list of pygame.Surface
    :returns: Новый список спрайтов, отражённых по горизонтали.
    :rtype: list of pygame.Surface
    :raises TypeError: Если аргумент `sprites` не является списком или элементы списка не являются объектами `pygame.Surface`.
    """
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    """
    Загружает листы спрайтов из указанной папки, разбивает изображения на спрайты
    заданных размеров и сохраняет их в словарь, с возможностью отражать их по горизонтали.

    :param dir1: Название первой папки в пути к спрайтам.
    :type dir1: str
    :param dir2: Название второй папки в пути к спрайтам.
    :type dir2: str
    :param width: Ширина каждого спрайта.
    :type width: int
    :param height: Высота каждого спрайта.
    :type height: int
    :param direction: Флаг, определяющий, нужно ли создавать зеркальные спрайты (для направления "left").
    :type direction: bool, по умолчанию False
    :returns: Словарь с загруженными и разбитыми спрайтами.
    :rtype: dict
    :raises FileNotFoundError: Если указанные папки или файлы не существуют.
    :raises pygame.error: Если возникла ошибка при загрузке изображения.
    :raises ValueError: Если изображения не соответствуют заданной ширине и высоте.
    """
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    """
    Загружает блок из файла "Terrain.png", обрезает его по заданному размеру и возвращает 
    увеличенную версию этого блока.

    :param size: Размер блока (ширина и высота), который нужно извлечь из изображения.
    :type size: int
    :returns: Увеличенная версия блока в виде объекта `pygame.Surface`.
    :rtype: pygame.Surface
    :raises pygame.error: Если изображение "Terrain.png" не удаётся загрузить.
    :raises ValueError: Если размер блока больше доступного размера в изображении.
    """
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    """
    Класс игрока первого персонажа, наследующий от pygame.sprite.Sprite.

    :param x: Начальная позиция по оси X.
    :type x: int
    :param y: Начальная позиция по оси Y.
    :type y: int
    :param width: Ширина игрока.
    :type width: int
    :param height: Высота игрока.
    :type height: int
    """
    GRAVITY = 1
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        self.SPRITES = load_sprite_sheets("MainCharacters", f"{skin}", 32, 32, True)
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"


        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Player_2(pygame.sprite.Sprite):
    """
    Класс игрока второго персонажа, наследующий от pygame.sprite.Sprite.

    :param x: Начальная позиция по оси X.
    :type x: int
    :param y: Начальная позиция по оси Y.
    :type y: int
    :param width: Ширина игрока.
    :type width: int
    :param height: Высота игрока.
    :type height: int
    """
    GRAVITY = 1
    ANIMATION_DELAY = 2

    def __init__(self, x, y, width, height):
        self.SPRITES = load_sprite_sheets("MainCharacters", f"{skin_2}", 32, 32, True)
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx_2, dy_2):
        self.rect.x += dx_2
        self.rect.y += dy_2

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1
    
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet == "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"


        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)


    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))



class Object(pygame.sprite.Sprite):
    """
    Класс объекта, наследующий от pygame.sprite.Sprite.

    :param x: Начальная позиция по оси X.
    :type x: int
    :param y: Начальная позиция по оси Y.
    :type y: int
    :param width: Ширина объекта.
    :type width: int
    :param height: Высота объекта.
    :type height: int
    :param name: Имя объекта (по умолчанию None).
    :type name: str or None
    """
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Fruit(Object):
    """
    Класс фрукта, наследующий от класса Object.

    :param x: Начальная позиция по оси X.
    :type x: int
    :param y: Начальная позиция по оси Y.
    :type y: int
    :param width: Ширина фрукта.
    :type width: int
    :param height: Высота фрукта.
    :type height: int
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fruit")
        fruit_image = pygame.image.load(join("assets", "items", "fruits", "Mashroom.png")).convert_alpha()
        self.image = pygame.transform.scale(fruit_image, (width, height))
        self.mask = pygame.mask.from_surface(self.image)


class Block(Object):
    """
    Класс блока, наследующий от класса Object.

    :param x: Начальная позиция по оси X.
    :type x: int
    :param y: Начальная позиция по оси Y.
    :type y: int
    :param size: Размер блока (ширина и высота одинаковы).
    :type size: int
    """
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Mob(Object):
    """
    Класс моба (зомби), наследующий от класса Object.

    :param x: Начальная позиция по оси X.
    :type x: int
    :param y: Начальная позиция по оси Y.
    :type y: int
    :param width: Ширина моба.
    :type width: int
    :param height: Высота моба.
    :type height: int
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "zombi")
        zombie_image = pygame.image.load(join("assets", "Items", "Fruits", "zombi.png")).convert_alpha()
        self.image = pygame.transform.scale(zombie_image, (width, height))
        self.mask = pygame.mask.from_surface(self.image)


class Buff(Object):
    """
    Класс баффа (предмета), наследующий от класса Object.

    :param x: Начальная позиция по оси X.
    :type x: int
    :param y: Начальная позиция по оси Y.
    :type y: int
    :param width: Ширина буфера.
    :type width: int
    :param height: Высота буфера.
    :type height: int
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "buff")
        buff_image = pygame.image.load(join("assets", "Traps", "Sand Mud Ice", "Ice Particle.png")).convert_alpha()
        self.image = pygame.transform.scale(buff_image, (width, height))
        self.mask = pygame.mask.from_surface(self.image)


class Button():
    """
    Класс кнопки для интерфейса.

    :param x: Начальная позиция по оси X.
    :type x: int
    :param y: Начальная позиция по оси Y.
    :type y: int
    :param image: Изображение кнопки.
    :type image: pygame.Surface
    :param scale: Масштаб изображения кнопки.
    :type scale: float
    """

    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        """
        Отображает изображение кнопки на поверхности и обрабатывает взаимодействие с мышью.

        :param surface: Поверхность, на которой будет отрисована кнопка.
        :type surface: pygame.Surface
        :returns: Логическое значение, указывающее, была ли нажата кнопка.
        :rtype: bool
        :raises TypeError: Если surface не является экземпляром pygame.Surface.
        """
        action = False

        pos = pygame.mouse.get_pos()


        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False


        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action



def get_background(name):
    """
    Загружает изображение фона по имени файла и создает список позиций для его 
    повторяющихся плиток, чтобы покрыть весь экран.

    :param name: Имя файла изображения фона.
    :type name: str
    :returns: Кортеж из списка позиций для плиток фона и самого изображения.
    :rtype: tuple (list, pygame.Surface)
    :raises pygame.error: Если изображение не удаётся загрузить.
    :raises FileNotFoundError: Если файл с указанным именем не найден.
    :raises AttributeError: Если `WIDTH` или `HEIGHT` не определены.
    """
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, player_2, objects, offset_x, fruits_collected):
    """
    Отображает элементы игры на экране.

    Рисует фон, объекты, игроков и текст с количеством собранных фруктов.

    :param window: Окно для отрисовки элементов игры.
    :type window: pygame.Surface
    :param background: Список тайлов фона для отрисовки.
    :type background: list
    :param bg_image: Изображение фона.
    :type bg_image: pygame.Surface
    :param player: Первый игрок для отрисовки.
    :type player: Player
    :param player_2: Второй игрок для отрисовки.
    :type player_2: Player_2
    :param objects: Список объектов для отрисовки.
    :type objects: list
    :param offset_x: Смещение по оси X для корректного отображения объектов.
    :type offset_x: int
    :param fruits_collected: Количество собранных фруктов.
    :type fruits_collected: int
    """
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    player_2.draw(window, offset_x)
    font = pygame.font.SysFont("comicsans", 30)
    text = font.render(f"Fruits Collected: {fruits_collected}/3", True, (255, 255, 255))
    window.blit(text, (10, 10))

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    """
    Обрабатывает вертикальные столкновения игрока с объектами. В зависимости от направления 
    перемещения (dy), корректирует позицию игрока и вызывает соответствующие методы 
    для приземления или столкновения с головой.

    :param player: Объект игрока, с которым проверяются столкновения.
    :type player: pygame.sprite.Sprite (или объект, поддерживающий метод collide_mask)
    :param objects: Список объектов, с которыми проверяются столкновения.
    :type objects: list
    :param dy: Направление и расстояние перемещения по вертикали.
    :type dy: int или float
    :returns: Список объектов, с которыми произошло столкновение.
    :rtype: list
    :raises TypeError: Если аргумент `objects` не является списком или если элементы 
        списка не являются объектами класса, поддерживающими метод `collide_mask`.
    :raises AttributeError: Если у объектов `player` или элементов в `objects` нет метода `collide_mask`.
    """
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    """
    Проверяет столкновение игрока с объектами при перемещении по оси X. Игрок временно 
    перемещается, чтобы проверить столкновение, после чего его позиция возвращается обратно.

    :param player: Объект игрока, с которым проверяются столкновения.
    :type player: pygame.sprite.Sprite (или объект, поддерживающий метод `move` и `update`)
    :param objects: Список объектов, с которыми проверяются столкновения.
    :type objects: list
    :param dx: Расстояние перемещения игрока по оси X.
    :type dx: int или float
    :returns: Объект, с которым произошло столкновение, или `None`, если столкновений не было.
    :rtype: pygame.sprite.Sprite или None
    :raises TypeError: Если аргумент `objects` не является списком или если элементы 
        списка не являются объектами, поддерживающими метод `collide_mask`.
    :raises AttributeError: Если у объектов `player` или элементов в `objects` нет метода `move` или `collide_mask`.
    """
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, player_2, objects):

    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    player_2.x_vel = 0
    collide_left_2 = collide(player_2, objects, -PLAYER_VEL * 2)
    collide_right_2 = collide(player_2, objects, PLAYER_VEL * 2)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)
    if keys[pygame.K_LEFT] and not collide_left_2:
        player_2.move_left(PLAYER_VEL)
    elif keys[pygame.K_RIGHT] and not collide_right_2:
        player_2.move_right(PLAYER_VEL)


def show_you_win(window):
    font = pygame.font.SysFont("Arial", 50)
    win_text = font.render("You Win!", True, (0, 255, 0))
    window.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 4))
    pygame.display.update()
    pygame.time.delay(2000)


def show_game_over(window):
    font = pygame.font.SysFont("Arial", 50)
    lose_text = font.render("You Lose!", True, (255, 0, 0))
    window.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, HEIGHT // 4))
    pygame.display.update()
    pygame.time.delay(1000)


def level1(window):
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    round_time = 100

    background, bg_image = get_background("Pink.png")

    fruits_collected = 0
    coll_mobs = 0
    dead_mobs = 0
    eat_buff = 0

    offset_x = -1500
    scroll_area_width = 500

    block_size = 96

    player = Player(-1000, 300, 50, 50)
    player_2 = Player_2(-900, 300, 50, 50)
    floor = [
        Block(i * block_size,
              HEIGHT - block_size if not (-1 <= i <= 1 or 10 <= i <= 15 or 16 <= i <= 22) else HEIGHT, block_size
              ) for i in range(-WIDTH // block_size, (WIDTH * 3) // block_size)]

    platform1 = Block(block_size * 2, HEIGHT - block_size * 2, block_size)
    platform12 = Block(block_size * 2, HEIGHT - block_size * 5, block_size)
    platform13 = Block(block_size * -2, HEIGHT - block_size * 5, block_size)
    platform2 = Block(block_size * 5, HEIGHT - block_size * 4, block_size)
    platform32 = Block(block_size * 9, HEIGHT - block_size * 5, block_size)
    platform33 = Block(block_size * 9, HEIGHT - block_size * 4, block_size)
    platform34 = Block(block_size * 9, HEIGHT - block_size * 3, block_size)
    platform35 = Block(block_size * 9, HEIGHT - block_size * 2, block_size)
    platform4 = Block(block_size * 13, HEIGHT - block_size * 4, block_size)
    platform5 = Block(block_size * 16, HEIGHT - block_size * 2, block_size)
    platform6 = Block(block_size * 10, HEIGHT - block_size * 2, block_size)
    platform7 = Block(block_size * 19, HEIGHT - block_size * 3, block_size)
    platform8 = Block(block_size * 22, HEIGHT - block_size * 5, block_size)


    Marshroom1 = Fruit(block_size * 10.4, HEIGHT - block_size * 1.80 - 48, 32, 32)
    Marshroom2 = Fruit(block_size * 22.5, HEIGHT - block_size * 4.8 - 48, 32, 32)
    Marshroom3 = Fruit(block_size * 7, HEIGHT - block_size * 0.85 - 48, 32, 32)


    mob1 = Mob(block_size * 9.3, HEIGHT - block_size * 5.5 - 32, 64, 64)

    buff1 = Buff(block_size * -1.8, HEIGHT - block_size * 5 - 48, 64, 64)

    objects = [*floor, mob1, buff1, Marshroom1, Marshroom2, Marshroom3, platform1, platform12, platform13,
               platform2, platform32, platform33, platform34, platform35, platform4, platform5, platform6,
               platform7, platform8]


    run = True

    while run:
        clock.tick(FPS)

        seconds_passed = (pygame.time.get_ticks() - start_time) / 1000
        remaining_time = round_time - seconds_passed
        if remaining_time <= 0:
            show_game_over(window)
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_SPACE and player_2.jump_count < 2:
                    player_2.jump()
                if event.key == pygame.K_ESCAPE:
                    run = False
            if fruits_collected == 3 and dead_mobs == 1:
                show_you_win(window)
                run = False
            if coll_mobs >= 1:
                show_game_over(window)
                run = False
        if (player.rect.bottom > 630) or (player_2.rect.bottom > 630):
            show_game_over(window)
            run = False

        player.loop(FPS)
        player_2.loop(FPS)
        for obj in objects[:]:
            if isinstance(obj, Fruit) and (pygame.sprite.collide_mask(player, obj)):
                objects.remove(obj)
                fruits_collected += 1

        for obj in objects[:]:
            if isinstance(obj, Mob) and (pygame.sprite.collide_mask(player, obj) or pygame.sprite.collide_mask(player_2, obj)) and buff1 in objects:
                coll_mobs += 1

        for obj in objects[:]:
            if isinstance(obj, Mob) and (pygame.sprite.collide_mask(player_2, obj)) and buff1 not in objects:
                objects.remove(obj)
                dead_mobs += 1

        for obj in objects[:]:
            if isinstance(obj, Buff) and (pygame.sprite.collide_mask(player_2, obj)):
                objects.remove(obj)
                eat_buff += 1

        handle_move(player, player_2, objects)
        handle_vertical_collision(player, objects, player.y_vel)
        handle_vertical_collision(player_2, objects, player_2.y_vel)
        draw(window, background, bg_image, player, player_2, objects, offset_x, fruits_collected)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel


def level2(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Green.png")

    start_time = pygame.time.get_ticks()
    round_time = 100

    offset_x = -1500
    scroll_area_width = 500

    block_size = 96

    player = Player(-900, 500, 50, 50)
    player_2 = Player_2(-800, 500, 50, 50)

    coll_mobs = 0
    dead_mobs = 0
    eat_buff = 0
    fruits_collected = 0

    floor = [
        Block(
            i * block_size,
            HEIGHT - block_size if not (
                    -1 <= i <= 1 or 6 <= i <= 8 or 10 <= i <= 15 or 21 <= i <= 23 or 25 <= i <= 26 or 27 <= i <= 28) else HEIGHT,
            block_size
        )
        for i in range(-WIDTH // block_size, (WIDTH * 3) // block_size)
    ]

    platformm103 = Block(block_size * -10, HEIGHT - block_size * 3, block_size)
    platformm95 = Block(block_size * -8, HEIGHT - block_size * 5, block_size)
    platformm112 = Block(block_size * -11, HEIGHT - block_size * 2, block_size)
    platformm113 = Block(block_size * -11, HEIGHT - block_size * 3, block_size)
    platformm114 = Block(block_size * -11, HEIGHT - block_size * 4, block_size)
    platformm115 = Block(block_size * -11, HEIGHT - block_size * 5, block_size)
    platformm116 = Block(block_size * -11, HEIGHT - block_size * 6, block_size)
    platformm117 = Block(block_size * -11, HEIGHT - block_size * 7, block_size)
    platform22 = Block(block_size * 2, HEIGHT - block_size * 2, block_size)
    platform54 = Block(block_size * 5, HEIGHT - block_size * 4, block_size)
    platform96 = Block(block_size * 9, HEIGHT - block_size * 6, block_size)
    platform134 = Block(block_size * 13, HEIGHT - block_size * 4, block_size)
    platform162 = Block(block_size * 16, HEIGHT - block_size * 2, block_size)
    platform196 = Block(block_size * 19, HEIGHT - block_size * 6, block_size)
    platform204 = Block(block_size * 20, HEIGHT - block_size * 4, block_size)
    platform301 = Block(block_size * 30, HEIGHT - block_size * 1, block_size)
    platform302 = Block(block_size * 30, HEIGHT - block_size * 2, block_size)
    platform303 = Block(block_size * 30, HEIGHT - block_size * 3, block_size)
    platform304 = Block(block_size * 30, HEIGHT - block_size * 4, block_size)
    platform305 = Block(block_size * 30, HEIGHT - block_size * 5, block_size)
    platform306 = Block(block_size * 30, HEIGHT - block_size * 6, block_size)
    platform307 = Block(block_size * 30, HEIGHT - block_size * 7, block_size)

    apple1 = Fruit(block_size * 9, HEIGHT - block_size * 0.85 - 48, 32, 32)
    apple2 = Fruit(block_size * 19, HEIGHT - block_size * 5.85 - 48, 32, 32)
    apple3 = Fruit(block_size * 29, HEIGHT - block_size * 0.85 - 48, 32, 32)

    mob1 = Mob(block_size * -4, HEIGHT - block_size * 0.85 - 82, 64, 64)
    mob2 = Mob(block_size * 5, HEIGHT - block_size * 0.85 - 82, 64, 64)

    buff1 = Buff(block_size * -8 + 16, HEIGHT - block_size * 4.85 - 82, 64, 64)

    objects = [*floor, apple1, apple2, apple3, mob1, mob2, buff1, platformm103, platformm95, platform196, platform204,
               platform301, platform302, platform303, platform304, platform305, platform306, platform307, platformm112,
               platformm113, platformm114, platformm115, platformm116, platformm117, platform22, platform54, platform96,
               platform134, platform162]

    run = True
    while run:
        clock.tick(FPS)

        seconds_passed = (pygame.time.get_ticks() - start_time) / 1000
        remaining_time = round_time - seconds_passed
        if remaining_time <= 0:
            show_game_over(window)
            run = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_SPACE and player_2.jump_count < 2:
                    player_2.jump()
                if event.key == pygame.K_ESCAPE:
                    run = False
                if fruits_collected == 3 and dead_mobs == 2:
                    show_you_win(window)
                    run = False
                if coll_mobs >= 1:
                    show_game_over(window)
                    run = False

        if (player.rect.bottom > 630) or (player_2.rect.bottom > 630):
            show_game_over(window)
            run = False

        player.loop(FPS)
        player_2.loop(FPS)

        for obj in objects[:]:
            if isinstance(obj, Fruit) and (pygame.sprite.collide_mask(player, obj)):
                objects.remove(obj)
                fruits_collected += 1
        for obj in objects[:]:
            if isinstance(obj, Mob) and (pygame.sprite.collide_mask(player, obj) or pygame.sprite.collide_mask(player_2, obj)) and buff1 in objects:
                coll_mobs += 1

        for obj in objects[:]:
            if isinstance(obj, Mob) and (pygame.sprite.collide_mask(player_2, obj)) and buff1 not in objects:
                objects.remove(obj)
                dead_mobs += 1

        for obj in objects[:]:
            if isinstance(obj, Buff) and (pygame.sprite.collide_mask(player_2, obj)):
                objects.remove(obj)
                eat_buff += 1

        handle_move(player, player_2, objects)
        handle_vertical_collision(player, objects, player.y_vel)
        handle_vertical_collision(player_2, objects, player_2.y_vel)
        draw(window, background, bg_image, player, player_2, objects, offset_x, fruits_collected)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel


def level3(window):
    clock = pygame.time.Clock()

    background, bg_image = get_background("Gray.png")

    block_size = 96

    player = Player(-920, 500, 50, 50)
    player_2 = Player_2(-960, 500, 50, 50)

    offset_x = -1500
    scroll_area_width = 500

    start_time = pygame.time.get_ticks()
    round_time = 100

    coll_mobs = 0
    dead_mobs = 0
    eat_buff = 0
    fruits_collected = 0

    floor = [
        Block(
            i * block_size,
            HEIGHT - block_size if not (
                    -9 <= i <= -8 or -6 <= i <= -5 or 0 <= i <= 3 or 12 <= i <= 14 or 16 <= i <= 18 or 27 <= i <= 30 or 32 <= i <= 35) else HEIGHT,
            block_size
        )
        for i in range(-WIDTH // block_size, (WIDTH * 4) // block_size)
    ]

    # Платформы

    platform4 = Block(block_size * 23, HEIGHT - block_size * 3, block_size)
    platform5 = Block(block_size * 21, HEIGHT - block_size * 5, block_size)
    platform93 = Block(block_size * 9, HEIGHT - block_size * 3, block_size)
    platformm112 = Block(block_size * -11, HEIGHT - block_size * 2, block_size)
    platformm113 = Block(block_size * -11, HEIGHT - block_size * 3, block_size)
    platformm114 = Block(block_size * -11, HEIGHT - block_size * 4, block_size)
    platformm115 = Block(block_size * -11, HEIGHT - block_size * 5, block_size)
    platformm116 = Block(block_size * -11, HEIGHT - block_size * 6, block_size)
    platformm117 = Block(block_size * -11, HEIGHT - block_size * 7, block_size)
    platformm402 = Block(block_size * 40, HEIGHT - block_size * 2, block_size)
    platformm403 = Block(block_size * 40, HEIGHT - block_size * 3, block_size)
    platformm404 = Block(block_size * 40, HEIGHT - block_size * 4, block_size)
    platformm405 = Block(block_size * 40, HEIGHT - block_size * 5, block_size)
    platformm406 = Block(block_size * 40, HEIGHT - block_size * 6, block_size)
    platformm407 = Block(block_size * 40, HEIGHT - block_size * 7, block_size)

    apple1 = Fruit(block_size * 31 + 32, HEIGHT - block_size - 32, 32, 32)
    apple2 = Fruit(block_size * 9 + 32, HEIGHT - block_size * 3 - 32, 32, 32)
    apple3 = Fruit(block_size * 23 + 32, HEIGHT - block_size * 3 - 32, 32, 32)

    mob1 = Mob(block_size * 7, HEIGHT - block_size - 64, 64, 64)
    mob2 = Mob(block_size * 21, HEIGHT - block_size - 64, 64, 64)
    mob3 = Mob(block_size * 39, HEIGHT - block_size - 64, 64, 64)

    buff1 = Buff(block_size * 21 + 16, HEIGHT - block_size * 6 - 64, 64, 64)

    objects = [*floor, buff1, mob1, mob2, mob3, apple1, apple2, apple3, platformm112, platformm113, platformm114,
               platformm115, platformm116, platformm117, platform93, platform4, platform5, platformm402, platformm403,
               platformm404, platformm405, platformm406, platformm407]

    run2 = True
    while run2:
        clock.tick(FPS)

        seconds_passed = (pygame.time.get_ticks() - start_time) / 1000
        remaining_time = round_time - seconds_passed
        if remaining_time <= 0:
            show_game_over(window)
            run2 = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run2 = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_SPACE and player_2.jump_count < 2:
                    player_2.jump()
                if event.key == pygame.K_ESCAPE:
                    run2 = False
            if fruits_collected == 3 and dead_mobs == 3:
                show_you_win(window)
                run2 = False
            if coll_mobs >= 1:
                show_game_over(window)
                run2 = False

        if (player.rect.bottom > 645) or (player_2.rect.bottom > 645):
            show_game_over(window)
            run2 = False

        player.loop(FPS)
        player_2.loop(FPS)

        for obj in objects[:]:
            if isinstance(obj, Fruit) and (pygame.sprite.collide_mask(player, obj)):
                objects.remove(obj)
                fruits_collected += 1
        for obj in objects[:]:
            if isinstance(obj, Mob) and (pygame.sprite.collide_mask(player, obj) or pygame.sprite.collide_mask(player_2, obj)) and buff1 in objects:
                coll_mobs += 1

        for obj in objects[:]:
            if isinstance(obj, Mob) and (pygame.sprite.collide_mask(player_2, obj)) and buff1 not in objects:
                objects.remove(obj)
                dead_mobs += 1

        for obj in objects[:]:
            if isinstance(obj, Buff) and (pygame.sprite.collide_mask(player_2, obj)):
                objects.remove(obj)
                eat_buff += 1

        handle_move(player, player_2, objects)
        handle_vertical_collision(player, objects, player.y_vel)
        handle_vertical_collision(player_2, objects, player_2.y_vel)
        draw(window, background, bg_image, player, player_2, objects, offset_x, fruits_collected)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel


level1_img = pygame.image.load("assets/Menu/Levels/01.png")
level1_button = Button(150, 280, level1_img, 4)

level2_img = pygame.image.load("assets/Menu/Levels/02.png")
level2_button = Button(250, 280, level2_img, 4)

level3_img = pygame.image.load("assets/Menu/Levels/03.png")
level3_button = Button(350, 280, level3_img, 4)

level41_img = pygame.image.load("assets/MainCharacters/MaskDude/jump.png")
skin1_button = Button(550, 280, level41_img, 2)
skin1_button_2 = Button(550, 380, level41_img, 2)

level42_img = pygame.image.load("assets/MainCharacters/NinjaFrog/jump.png")
skin2_button = Button(650, 280, level42_img, 2)
skin2_button_2 = Button(650, 380, level42_img, 2)

level43_img = pygame.image.load("assets/MainCharacters/PinkMan/jump.png")
skin3_button = Button(750, 280, level43_img, 2)
skin3_button_2 = Button(750, 380, level43_img, 2)

level44_img = pygame.image.load("assets/MainCharacters/VirtualGuy/jump.png")
skin4_button = Button(850, 280, level44_img, 2)
skin4_button_2 = Button(850, 380, level44_img, 2)

run_52 = True

if __name__ == "__main__":
    while run_52:
        window.fill("Black")

        if skin4_button.draw(window):
            skin = "VirtualGuy"
            print(skin)
        if skin4_button_2.draw(window):
            skin_2 = "VirtualGuy"
            print(skin_2)
        

        if skin3_button.draw(window):
            skin = "PinkMan"
            print(skin)
        if skin3_button_2.draw(window):
            skin_2 = "PinkMan"
            print(skin_2)

        if skin1_button.draw(window):
            skin = "MaskDude"
            print(skin)
        if skin1_button_2.draw(window):
            skin_2 = "MaskDude"
            print(skin_2)
        if skin2_button.draw(window):
            skin = "NinjaFrog"
            print(skin)
        if skin2_button_2.draw(window):
            skin_2 = "NinjaFrog"
            print(skin_2)

        if level1_button.draw(window):
            run_game = True
            while run_game:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run_game = False
                        run = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            run_game = False
                pygame.display.update()

                level1(window)
                run_game = False

        if level2_button.draw(window):
            run_game2 = True
            while run_game2:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run_game = False
                        run = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            run_game2 = False
                pygame.display.update()

                level2(window)
                run_game2 = False

        if level3_button.draw(window):
            run_game3 = True
            while run_game3:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run_game = False
                        run = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            run_game3 = False
                pygame.display.update()

                level3(window)
                run_game3 = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_52 = False
        pygame.display.update()
    pygame.quit()
    quit()
    main()