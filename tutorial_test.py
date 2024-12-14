

import pygame
import unittest
from unittest.mock import patch, MagicMock
from os.path import join
from unittest.mock import Mock
from os import listdir
from os.path import isfile, join
from tutorial import flip, check_buff_collision, check_fruit_collision, get_block, collide, get_background, handle_vertical_collision, check_mob_collision, WIDTH, HEIGHT, Player, Player_2, Buff, Button, Object, Fruit, Mob


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

if __name__ == '__main__':
    pygame.init()
    unittest.main()
    pygame.quit()

class TestCheckBuffCollision(unittest.TestCase):

    @patch('pygame.sprite.collide_mask')
    def test_buff_collision_positive(self, mock_collide_mask):
        mock_collide_mask.return_value = True
        
        player = Player(100, 200, 50, 50)
        player_2 = Player(200, 200, 50, 50)
        
        buff = Buff(100, 200, 50, 50)
        objects = [buff]
        
        result = check_buff_collision(player, player_2, objects)
        
        self.assertEqual(result, 1)
        self.assertNotIn(buff, objects)

    @patch('pygame.sprite.collide_mask')
    def test_buff_collision_negative(self, mock_collide_mask):
        mock_collide_mask.return_value = False
        
        player = Player(100, 200, 50, 50)
        player_2 = Player(200, 200, 50, 50)
        
        buff = Buff(100, 2000, 50, 50)
        objects = [buff]
        
        result = check_buff_collision(player, player_2, objects)
        
        self.assertEqual(result, 1)
        self.assertIn(buff, objects)

if __name__ == '__main__':
    unittest.main()

class TestCheckFruitCollision(unittest.TestCase):

    @patch('pygame.sprite.collide_mask')
    def test_fruit_collision_positive(self, mock_collide_mask):
        mock_collide_mask.return_value = True
        
        player = Player(100, 200, 50, 50)
        player_2 = Player(200, 200, 50, 50)
        
        fruit = Fruit(100, 200, 50, 50)
        objects = [fruit]
        
        result = check_fruit_collision(player, player_2, objects)
        
        self.assertEqual(result, 1)
        self.assertNotIn(fruit, objects)

    @patch('pygame.sprite.collide_mask')
    def test_fruit_collision_negative(self, mock_collide_mask):
        mock_collide_mask.return_value = False
        
        player = Player(100, 200, 50, 50)
        player_2 = Player(200, 200, 50, 50)
        
        fruit = Fruit(1000, 100, 50, 50)
        objects = [fruit]
        
        result = check_fruit_collision(player, player_2, objects)
        
        self.assertEqual(result, 0)
        self.assertIn(fruit, objects)

if __name__ == '__main__':
    unittest.main()

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

class TestButtonDraw(unittest.TestCase):

    @patch("pygame.mouse.get_pos")
    @patch("pygame.mouse.get_pressed")
    def test_draw_button_clicked(self, mock_get_pressed, mock_get_pos):
        image = pygame.Surface((100, 50))
        image.fill((255, 0, 0))
        button = Button(50, 50, image, 1)

        mock_get_pos.return_value = (75, 75)
        mock_get_pressed.return_value = (1, 0, 0)

        surface = pygame.Surface((200, 200))

        action = button.draw(surface)

        self.assertTrue(action)

    @patch("pygame.mouse.get_pos")
    @patch("pygame.mouse.get_pressed")
    def test_draw_button_not_clicked(self, mock_get_pressed, mock_get_pos):
        image = pygame.Surface((100, 50))
        image.fill((0, 255, 0))
        button = Button(50, 50, image, 1)

        mock_get_pos.return_value = (200, 200)
        mock_get_pressed.return_value = (0, 0, 0)

        surface = pygame.Surface((200, 200))

        action = button.draw(surface)

        self.assertFalse(action)

if __name__ == "__main__":
    pygame.init()
    unittest.main()
    pygame.quit()


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