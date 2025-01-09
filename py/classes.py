import pygame


class Enemy_Group(pygame.sprite.Group):
    pass


class Spaceship(pygame.sprite.Sprite):

    def __init__(self, x, y, wall, image, reload, bullet_group, target_group):
        super().__init__()
        image = pygame.image.load(image)
        self.image = image
        self.rect = self.image.get_rect()

        self.maas = pygame.mask.from_surface(self.image)

        self.wall_x_min = wall[0]
        self.wall_y_min = wall[1]
        self.wall_x_max = wall[2]
        self.wall_y_max = wall[3]

        self.rect.x = x - self.rect.width // 2
        self.rect.y = y - self.rect.height // 2

        self.reload = reload
        self.bullet_group = bullet_group
        self.target_group = target_group

        self.clock = pygame.time.Clock()
        self.wait = 0

    def move(self, x, y):
        if self.check_move(x, y):
            self.rect.x += x
            self.rect.y += y

    def check_move(self, x, y):
        return self.rect.x + x >= self.wall_x_min and self.rect.y + y >= self.wall_y_min and \
               self.rect.x + self.rect.width + x <= self.wall_x_max and \
               self.rect.y + self.rect.height + y <= self.wall_y_max


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction, image, speed, target_group):
        super().__init__()
        image = pygame.image.load(image)
        self.image = image
        self.rect = self.image.get_rect()
        
        self.rect.x = x - self.rect.width // 2
        self.rect.y = y - self.rect.height // 2
        
        self.direction = direction
        self.speed = speed
        self.target_group = target_group
    
    def update(self):
        self.rect.y += self.speed * self.direction[0]
        self.rect.x += self.speed * self.direction[1]

        for sprite in Enemy_Group.sprites(self.target_group):
            if pygame.sprite.collide_mask(self, sprite):
                self.kill()
                break


class Player_SpaceShip1(Spaceship):
    
    def __init__(self, x, y, wall, bullet_group, target_group):
        super().__init__(x, y, wall, 'data\\image\\player1\\rocket.png', 200, bullet_group, target_group)

    def shoot(self):
        self.wait += self.clock.tick()
        if self.wait > self.reload:
            self.wait = 0
            bullet = Player_Bullet1(self.rect.x + self.rect.width // 2, self.rect.y - self.rect.height // 2, self.target_group)
            self.bullet_group.add(bullet)


class Player_Bullet1(Bullet):
    
    def __init__(self, x, y, target_group):
        super().__init__(x, y, (-1, 0), 'data\\image\\player1\\cactus.png', 5, target_group)
        

class Enemy1(Spaceship):

    def __init__(self, x, y, wall, bullet_group, target_group):
        super().__init__(x, y, wall, 'data\\image\\enemy1\\enemy.png', 2000, bullet_group, target_group)

    def shoot(self):
        self.wait += self.clock.tick()
        if self.wait > self.reload:
            self.wait = 0
            bullet = Enemy_Bullet1(self.rect.x + self.rect.width // 2, self.rect.y - self.rect.height // 2, self.target_group)
            self.bullet_group.add(bullet)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.shoot()


class Enemy_Bullet1(Bullet):

    def __init__(self, x, y, target_group):
        super().__init__(x, y, (1, 0), 'data\\image\\enemy1\\bullet.png', 10, target_group)


