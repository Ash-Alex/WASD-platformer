

import pygame
import unittest
from unittest.mock import patch, MagicMock
from os.path import join
from unittest.mock import Mock
from os import listdir
from os.path import isfile, join


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

class TestFlipFunction(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.sprite1 = pygame.Surface((10, 10))
        self.sprite1.fill((255, 0, 0))
        self.sprite2 = pygame.Surface((20, 20))
        self.sprite2.fill((0, 255, 0))
        self.sprites = [self.sprite1, self.sprite2]

    def test_flip_positive(self):
        flipped_sprites = flip(self.sprites)
        self.assertEqual(len(flipped_sprites), len(self.sprites))
        for flipped in flipped_sprites:
            self.assertIsInstance(flipped, pygame.Surface)

    def test_flip_negative(self):
        with self.assertRaises(TypeError):
            flip(None)

if __name__ == "__main__":
    unittest.main()


def check_buff_collision(player, player_2, objects):
    eat_buff = 1
    for obj in objects[:]:
        if isinstance(obj, Buff) and pygame.sprite.collide_mask(player, player_2, obj):
            objects.remove(obj)
    return eat_buff

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

class Buff(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

class TestCheckBuffCollision(unittest.TestCase):

    @patch('pygame.sprite.collide_mask')
    def test_buff_collision_positive(self, mock_collide_mask):
        mock_collide_mask.return_value = True
        
        player = Player()
        player_2 = Player()
        
        buff = Buff()
        objects = [buff]
        
        result = check_buff_collision(player, player_2, objects)
        
        self.assertEqual(result, 1)
        self.assertNotIn(buff, objects)

    @patch('pygame.sprite.collide_mask')
    def test_buff_collision_negative(self, mock_collide_mask):
        mock_collide_mask.return_value = False
        
        player = Player()
        player_2 = Player()
        
        buff = Buff()
        objects = [buff]
        
        result = check_buff_collision(player, player_2, objects)
        
        self.assertEqual(result, 1)
        self.assertIn(buff, objects)

if __name__ == '__main__':
    unittest.main()




def check_fruit_collision(player, player_2, objects):
    collected = 0
    for obj in objects[:]:
        if isinstance(obj, Fruit) and pygame.sprite.collide_mask(player, player_2, obj):
            objects.remove(obj)
            collected += 1
    return collected

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

class Fruit(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

class TestCheckFruitCollision(unittest.TestCase):

    @patch('pygame.sprite.collide_mask')
    def test_fruit_collision_positive(self, mock_collide_mask):
        mock_collide_mask.return_value = True
        
        player = Player()
        player_2 = Player()
        
        fruit = Fruit()
        objects = [fruit]
        
        result = check_fruit_collision(player, player_2, objects)
        
        self.assertEqual(result, 1)
        self.assertNotIn(fruit, objects)

    @patch('pygame.sprite.collide_mask')
    def test_fruit_collision_negative(self, mock_collide_mask):
        mock_collide_mask.return_value = False
        
        player = Player()
        player_2 = Player()
        
        fruit = Fruit()
        objects = [fruit]
        
        result = check_fruit_collision(player, player_2, objects)
        
        self.assertEqual(result, 0)
        self.assertIn(fruit, objects)

    @patch('pygame.sprite.collide_mask')
    def test_multiple_fruits(self, mock_collide_mask):
        mock_collide_mask.return_value = True
        
        player = Player()
        player_2 = Player()
        
        fruit1 = Fruit()
        fruit2 = Fruit()
        fruit3 = Fruit()
        objects = [fruit1, fruit2, fruit3]
        
        result = check_fruit_collision(player, player_2, objects)
        
        self.assertEqual(result, 3)
        self.assertNotIn(fruit1, objects)
        self.assertNotIn(fruit2, objects)
        self.assertNotIn(fruit3, objects)

if __name__ == '__main__':
    unittest.main()


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class TestGetBlock(unittest.TestCase):

    @patch("pygame.image.load")
    @patch("pygame.Surface")
    @patch("pygame.transform.scale2x")
    def test_get_block_success(self, mock_scale2x, mock_surface, mock_image_load):
        mock_image = MagicMock()
        mock_image.convert_alpha.return_value = mock_image
        mock_image_load.return_value = mock_image
        mock_surface_instance = MagicMock()
        mock_surface.return_value = mock_surface_instance
        mock_scale2x.return_value = mock_surface_instance

        size = 50
        result = get_block(size)

        mock_image_load.assert_called_once_with(join("assets", "Terrain", "Terrain.png"))
        mock_image.convert_alpha.assert_called_once()
        mock_surface.assert_called_once_with((size, size), pygame.SRCALPHA, 32)
        mock_surface_instance.blit.assert_called_once_with(mock_image, (0, 0), pygame.Rect(96, 0, size, size))
        mock_scale2x.assert_called_once_with(mock_surface_instance)
        self.assertEqual(result, mock_surface_instance)

    @patch("pygame.image.load")
    def test_get_block_image_not_found(self, mock_image_load):
        mock_image_load.side_effect = FileNotFoundError("Image file not found")

        with self.assertRaises(FileNotFoundError):
            get_block(50)

if __name__ == "__main__":
    unittest.main()



def collide(player, objects, dx):
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

class TestCollide(unittest.TestCase):

    @patch("pygame.sprite.collide_mask")
    def test_collide_success(self, mock_collide_mask):
        player = MagicMock()
        obj = MagicMock()

        mock_collide_mask.return_value = True

        objects = [obj]
        result = collide(player, objects, 5)

        mock_collide_mask.assert_called_once_with(player, obj)
        self.assertEqual(result, obj)

    @patch("pygame.sprite.collide_mask")
    def test_collide_no_collision(self, mock_collide_mask):
        player = MagicMock()
        obj = MagicMock()

        mock_collide_mask.return_value = False

        objects = [obj]
        result = collide(player, objects, 5)

        mock_collide_mask.assert_called_once_with(player, obj)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()



WIDTH = 800
HEIGHT = 600

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

class TestGetBackground(unittest.TestCase):

    @patch("pygame.image.load")
    def test_get_background_success(self, mock_image_load):
        mock_image = MagicMock()
        mock_image.get_rect.return_value = (0, 0, 100, 100)
        mock_image_load.return_value = mock_image

        tiles, image = get_background("background.png")

        mock_image_load.assert_called_once_with(join("assets", "Background", "background.png"))
        self.assertEqual(image, mock_image)

        expected_tiles = [(i * 100, j * 100) for i in range(WIDTH // 100 + 1) for j in range(HEIGHT // 100 + 1)]
        self.assertEqual(tiles, expected_tiles)

    @patch("pygame.image.load")
    def test_get_background_file_not_found(self, mock_image_load):
        mock_image_load.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError):
            get_background("background.png")

        mock_image_load.assert_called_once_with(join("assets", "Background", "background.png"))

if __name__ == "__main__":
    unittest.main()


def handle_vertical_collision(player, objects, dy):
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

class TestHandleVerticalCollision(unittest.TestCase):

    @patch("pygame.sprite.collide_mask")
    def test_handle_vertical_collision_success(self, mock_collide_mask):
        player = MagicMock()
        player.rect = MagicMock()
        obj1 = MagicMock()
        obj1.rect = MagicMock()

        mock_collide_mask.return_value = True

        objects = [obj1]
        dy = 5
        collided_objects = handle_vertical_collision(player, objects, dy)

        player.landed.assert_called_once()
        player.hit_head.assert_not_called()

        self.assertEqual(collided_objects, [obj1])

        self.assertEqual(player.rect.bottom, obj1.rect.top)

    @patch("pygame.sprite.collide_mask")
    def test_handle_vertical_collision_no_collision(self, mock_collide_mask):
        player = MagicMock()
        obj1 = MagicMock()

        mock_collide_mask.return_value = False

        objects = [obj1]
        dy = 5
        collided_objects = handle_vertical_collision(player, objects, dy)

        player.landed.assert_not_called()
        player.hit_head.assert_not_called()

        self.assertEqual(collided_objects, [])

if __name__ == "__main__":
    unittest.main()


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.clicked = False

    def draw(self, surface):
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


class TestButtonDraw(unittest.TestCase):

    @patch("pygame.mouse.get_pos")
    @patch("pygame.mouse.get_pressed")
    def test_draw_button_clicked(self, mock_get_pressed, mock_get_pos):
        image = MagicMock()
        image.get_rect.return_value = pygame.Rect(50, 50, 100, 50)
        button = Button(50, 50, image)

        mock_get_pos.return_value = (75, 75)
        mock_get_pressed.return_value = (1, 0, 0)

        surface = MagicMock()

        action = button.draw(surface)

        self.assertTrue(action)

        surface.blit.assert_called_once_with(image, (50, 50))

    @patch("pygame.mouse.get_pos")
    @patch("pygame.mouse.get_pressed")
    def test_draw_button_not_clicked(self, mock_get_pressed, mock_get_pos):
        image = MagicMock()
        image.get_rect.return_value = pygame.Rect(50, 50, 100, 50)
        button = Button(50, 50, image)

        mock_get_pos.return_value = (200, 200)
        mock_get_pressed.return_value = (0, 0, 0)

        surface = MagicMock()

        action = button.draw(surface)

        self.assertFalse(action)

        surface.blit.assert_called_once_with(image, (50, 50))


if __name__ == "__main__":
    unittest.main()



def check_mob_collision(player, player_2, objects):
    coll_mobs = 0
    for obj in objects[:]:
        if isinstance(obj, Mob) and (pygame.sprite.collide_mask(player, obj) or pygame.sprite.collide_mask(player_2, obj)):
            coll_mobs += 1
    return coll_mobs

class Mob(pygame.sprite.Sprite):
    pass

class TestCheckMobCollision(unittest.TestCase):
    def test_check_mob_collision_positive(self):
        player = MagicMock()
        player_2 = MagicMock()

        mob1 = MagicMock(spec=Mob)
        mob2 = MagicMock(spec=Mob)
        objects = [mob1, mob2]

        pygame.sprite.collide_mask = MagicMock(side_effect=lambda p, o: o in [mob1, mob2])

        result = check_mob_collision(player, player_2, objects)

        self.assertEqual(result, 2)

    def test_check_mob_collision_negative(self):
        player = MagicMock()
        player_2 = MagicMock()

        mob1 = MagicMock(spec=Mob)
        mob2 = MagicMock(spec=Mob)
        objects = [mob1, mob2]

        pygame.sprite.collide_mask = MagicMock(return_value=False)

        result = check_mob_collision(player, player_2, objects)

        self.assertEqual(result, 0)

if __name__ == "__main__":
    unittest.main()