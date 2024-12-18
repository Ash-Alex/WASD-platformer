import pygame
import unittest
from unittest.mock import patch, MagicMock
from os.path import join
from tutorial import flip, get_block, get_background, handle_vertical_collision, WIDTH, HEIGHT, Button


class TestFunctions(unittest.TestCase):

    @patch("pygame.sprite.collide_mask")
    def test_handle_vertical_collision_positive(self, mock_collide_mask):
        self.player = MagicMock()
        self.player.rect = pygame.Rect(0, 0, 50, 50)
        self.obj = MagicMock()
        self.obj.rect = pygame.Rect(0, 50, 50, 50)
        mock_collide_mask.return_value = True

        dy = 10
        result = handle_vertical_collision(self.player, [self.obj], dy)

        self.assertEqual(result, [self.obj])

        self.assertEqual(self.player.rect.bottom, self.obj.rect.top)
        self.player.landed.assert_called_once()
        self.player.hit_head.assert_not_called()

    @patch("pygame.sprite.collide_mask")
    def test_handle_vertical_collision_negative(self, mock_collide_mask):
        self.player = MagicMock()
        self.player.rect = pygame.Rect(0, 0, 50, 50)
        self.obj = MagicMock()
        self.obj.rect = pygame.Rect(0, 100, 50, 50)
        mock_collide_mask.return_value = False

        dy = 10
        result = handle_vertical_collision(self.player, [self.obj], dy)

        self.assertEqual(result, [])

        self.player.landed.assert_not_called()
        self.player.hit_head.assert_not_called()


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


    def test_flip_positive(self):
        self.sprite1 = pygame.Surface((10, 10))
        self.sprite1.fill((255, 0, 0))
        self.sprite2 = pygame.Surface((20, 20))
        self.sprite2.fill((0, 255, 0))
        self.sprites = [self.sprite1, self.sprite2]
        flipped_sprites = flip(self.sprites)
        self.assertEqual(len(flipped_sprites), len(self.sprites))
        for flipped in flipped_sprites:
            self.assertIsInstance(flipped, pygame.Surface)

    def test_flip_negative(self):
        with self.assertRaises(TypeError):
            flip(self)


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

        mock_get_pos.return_value = (75, 75)
        mock_get_pressed.return_value = (0, 0, 0)

        surface = pygame.Surface((200, 200))

        action = button.draw(surface)

        self.assertFalse(action)


if __name__ == "__main__":
    unittest.main()

