import pygame


with open('settings.txt', 'r', encoding='utf-8') as setting:
    dictionary = dict()
    for i in setting.readlines():
        i = i.split(':', 1)
        dictionary[i[0]] = dict([u.strip().split(': ') for u in i[1].split(', ')])
    
    for key in dictionary.keys():
        for key1 in dictionary[key].keys():
            dictionary[key][key1] = int(dictionary[key][key1])
    print(dictionary)

class Enemy_Group(pygame.sprite.Group):
    pass


class Spaceship(pygame.sprite.Sprite):

    def __init__(self, x, y, wall, image, reload, bullet_group, target_group, hp, speed):
        super().__init__()
        image = pygame.image.load(image)
        self.image = image
        self.rect = self.image.get_rect()

        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect.x = x - self.rect.width // 2
        self.rect.y = y - self.rect.height // 2

        self.wall_x_min = wall[0]
        self.wall_y_min = wall[1]
        self.wall_x_max = wall[2]
        self.wall_y_max = wall[3]

        self.reload = reload
        self.hp = hp
        self.speed = speed

        self.bullet_group = bullet_group
        self.target_group = target_group

        self.clock = pygame.time.Clock()
        self.wait = 0

    def move(self, x, y):
        x = self.speed * x
        y = self.speed * y
        if self.check_move(x, y):
            self.rect.x += x
            self.rect.y += y

    def hurt(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.death()

    def death(self):
        self.kill()

    def check_move(self, x, y):
        return self.rect.x + x >= self.wall_x_min and self.rect.y + y >= self.wall_y_min and \
               self.rect.x + self.rect.width + x <= self.wall_x_max and \
               self.rect.y + self.rect.height + y <= self.wall_y_max


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, wall, direction, image, speed, target_group, damage=1):
        super().__init__()
        image = pygame.image.load(image)
        self.image = image
        self.rect = self.image.get_rect()
        
        self.rect.x = x - self.rect.width // 2
        self.rect.y = y - self.rect.height // 2

        self.wall_x_max = wall[0]
        self.wall_y_max = wall[1]
        
        self.damage = damage
        self.direction = direction
        self.speed = speed
        self.target_group = target_group
    
    def update(self):
        self.rect.y += self.speed * self.direction[0]
        self.rect.x += self.speed * self.direction[1]

        if self.rect.x + self.rect.width < -100 or\
           self.rect.y + self.rect.height < -100 or\
           self.rect.x > self.wall_x_max + 100 or\
           self.rect.y > self.wall_y_max + 100:
            self.kill()
        
        for sprite in Enemy_Group.sprites(self.target_group):
            if pygame.sprite.collide_mask(self, sprite):
                sprite.hurt(self.damage)
                self.kill()


class Player_SpaceShip1(Spaceship):
    
    def __init__(self, x, y, wall, bullet_group, target_group):
        super().__init__(x, y, wall, 'data\\image\\player1\\rocket.png', dictionary['player1']['reload'], bullet_group, target_group, dictionary['player1']['hp'], dictionary['player1']['speed'])

    def shoot(self):
        self.wait += self.clock.tick()
        if self.wait > self.reload:
            self.wait = 0
            bullet = Player_Bullet1(self.rect.x + self.rect.width // 2, self.rect.y - self.rect.height // 2, (self.wall_x_max, self.wall_y_max), self.target_group, dictionary['player1']['damage'])
            self.bullet_group.add(bullet)


class Player_Bullet1(Bullet):
    
    def __init__(self, x, y, wall, target_group, damage):
        super().__init__(x, y, wall, (-1, 0), 'data\\image\\player1\\cactus.png', 5, target_group, damage)


class Enemy1(Spaceship):

    def __init__(self, x, y, wall, bullet_group, target_group):
        super().__init__(x, y, wall, 'data\\image\\enemy1\\enemy.png', dictionary['enemy1']['reload'], bullet_group, target_group, dictionary['enemy1']['hp'], dictionary['enemy1']['speed'])

    def shoot(self):
        self.wait += self.clock.tick()
        if self.wait > self.reload:
            self.wait = 0
            bullet = Enemy_Bullet1(self.rect.x + self.rect.width // 2, self.rect.y - self.rect.height // 2, (self.wall_x_max, self.wall_y_max), self.target_group, dictionary['enemy1']['damage'])
            self.bullet_group.add(bullet)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.shoot()


class Enemy_Bullet1(Bullet):

    def __init__(self, x, y, wall, target_group, damage):
        super().__init__(x, y, wall, (1, 0), 'data\\image\\enemy1\\bullet.png', 10, target_group, damage)


