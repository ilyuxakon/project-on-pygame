import re
import pygame


class Spaceship(pygame.sprite.Sprite):

    def __init__(self, x, y, wall, *group):
        super().__init__(*group)
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("green"), (20, 20), 20)
        self.rect = pygame.Rect(x, y, 40, 40)

        self.wall_x_min = wall[0]
        self.wall_y_min = wall[1]
        self.wall_x_max = wall[2]
        self.wall_y_max = wall[3]

    def move(self, x, y):
        if self.check_move(x, y):
            self.rect.x += x
            self.rect.y += y

    def check_move(self, x, y):
        return self.rect.x + x >= self.wall_x_min and self.rect.y + y >= self.wall_y_min and \
               self.rect.x + self.rect.width + x <= self.wall_x_max and \
               self.rect.y + self.rect.height + y <= self.wall_y_max
    
    def shoot(self):
        bullet = Bullet(self.rect.x + 15, self.rect.y - 10, -1)
        self.bullet_group.add(bullet)
            


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction, *group):
        super().__init__(*group)
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("purple"), (5, 5), 5)
        self.rect = pygame.Rect(x, y, 10, 10)

        self.direction = direction
    
    def update(self):
        self.rect.y += 2 * self.direction


def main():
    pygame.init()
    size = 1000, 1000
    screen = pygame.display.set_mode(size)

    clock = pygame.time.Clock()

    player_group = pygame.sprite.Group()
    player = Spaceship(100, 100, (0, 0, *size), player_group)

    player_group.add(player_group)
    player_group.draw(screen)

    bullet_up = pygame.sprite.Group()
    bullet_down = pygame.sprite.Group()

    player.bullet_group = bullet_up

    keys = {'up': False, 'down': False, 'left': False, 'right': False}

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    keys['up'] = True
                
                elif event.key == pygame.K_DOWN:
                    keys['down'] = True

                elif event.key == pygame.K_LEFT:
                    keys['left'] = True
                
                elif event.key == pygame.K_RIGHT:
                    keys['right'] = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    keys['up'] = False
                
                elif event.key == pygame.K_DOWN:
                    keys['down'] = False

                elif event.key == pygame.K_LEFT:
                    keys['left'] = False
                
                elif event.key == pygame.K_RIGHT:
                    keys['right'] = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot()

            elif event.type == pygame.QUIT:
                running = False

        if keys['up']: player.move(0, -5)
        if keys['down']: player.move(0, 5)
        if keys['left']: player.move(-5, 0)
        if keys['right']: player.move(5, 0)
        
        screen.fill(pygame.Color('black'))
        player_group.draw(screen)
        bullet_up.update()
        bullet_down.update()
        bullet_down.draw(screen)
        bullet_up.draw(screen)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()




if __name__ == '__main__':
    main()