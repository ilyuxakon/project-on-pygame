import pygame
import random
import animations
import get_settings

characteristic = get_settings.characteristic()

class Spaceship(pygame.sprite.Sprite):

    def __init__(self, x, y, wall, image, bullet_group, target_group, hp, speed):
        super().__init__()
        self.set_image(image)
        self.rect = self.image.get_rect()
        
        self.rect.x = x - self.rect.width // 2
        self.rect.y = y - self.rect.height // 2

        self.wall_x_min = wall[0]
        self.wall_y_min = wall[1]
        self.wall_x_max = wall[2]
        self.wall_y_max = wall[3]

        self.hp = hp
        self.speed = speed

        self.bullet_group = bullet_group
        self.target_group = target_group

    def set_image(self, image):
        image = pygame.image.load(image)
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)

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


class Player_Cannon(pygame.sprite.Sprite):

    def __init__(self, cannon_name, bullet_group, target_group, columns, rows):
        super().__init__()

        self.frames = animations.make_frames(characteristic[cannon_name]['filename'][0], columns, rows)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.flag = False

        self.bullet_group = bullet_group
        self.target_group = target_group
        self.reload = characteristic[cannon_name]['reload']
        self.current_reload = self.reload
        self.damage = characteristic[cannon_name]['damage']

        self.clock = pygame.time.Clock()
        self.wait = 0
        
    def shoot(self):
        if self.wait >= self.current_reload:
            self.wait = 0
            inaccuracy = random.randrange(-5, 6)
            self.current_reload = self.reload + (self.reload * inaccuracy * 0.1)
            self.flag = True

    def move(self, x, y):
        self.rect.x = x - self.rect.width // 2 + self.x
        self.rect.y = y - self.rect.height // 2 + self.y

    def update(self):
        self.wait += 1


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction, cannon_name, speed, target_group, damage, columns, rows):
        super().__init__()
        self.frames = animations.make_frames(characteristic[cannon_name]['filename'][1], columns, rows)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        
        self.rect.x = x - self.rect.width // 2
        self.rect.y = y - self.rect.height // 2
        
        self.damage = damage
        self.direction = direction
        self.speed = speed
        self.target_group = target_group

    def set_image(self, image):
        image = pygame.image.load(image)
        self.image = image
    
    def update(self):
        self.rect.y += self.speed * self.direction[0]
        self.rect.x += self.speed * self.direction[1]

        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.image = self.frames[self.current_frame]

        if self.rect.x + self.rect.width < -100 or\
           self.rect.y + self.rect.height < -100 or\
           self.rect.x > 4100 or\
           self.rect.y > 4100:
            self.kill()
            
        for sprite in self.target_group.sprites():
            if pygame.sprite.collide_mask(self, sprite):
                sprite.hurt(self.damage)
                self.kill()


class Enemy(Spaceship):

    def __init__(self, x, y, wall, enemy_name, bullet_group, target_group):
        super().__init__(x, y, wall, characteristic[enemy_name], bullet_group, target_group, characteristic[enemy_name]['hp'], characteristic[enemy_name]['speed'])
        self.reload = characteristic[enemy_name]['reload']
        self.current_reload = self.reload
        self.clock = pygame.time.Clock()
        self.wait = 0

    def shoot(self):
        self.wait += self.clock.tick()
        if self.wait > self.current_reload:
            self.wait = 0
            self.current_reload = self.reload + random.randrange(int(-0.1 *self.reload), int(0.1 * self.reload))

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.shoot()


class Player_SpaceShip(Spaceship):
    
    def __init__(self, x, y, wall, bullet_group, target_group, player_group, spaceship, cannon):
        super().__init__(x, y, wall, characteristic[spaceship]['filename'][0], bullet_group, target_group, characteristic[spaceship]['hp'], characteristic[spaceship]['speed'])
        self.stages = characteristic[spaceship]['filename'][1:]
        self.max_hp = self.hp

        self.cannon = cannon(bullet_group, target_group)
        self.cannon.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)
        player_group.add(self.cannon)

    def shoot(self):
        self.cannon.shoot()

    def hurt(self, damage):
        super().hurt(damage)
        print(self.hp)

        if 0.75 >= self.hp / self.max_hp > 0.5:
            self.set_image(self.stages[0])

        elif 0.5 >= self.hp / self.max_hp > 0.25:
            self.set_image(self.stages[1])

        elif 0.25 >= self.hp / self.max_hp:
            self.set_image(self.stages[2])

    def move(self, x, y):
        super().move(x, y)
        self.cannon.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)


class Auto_Cannon(Player_Cannon):

    def __init__(self, bullet_group, target_group):
        super().__init__('auto_cannon', bullet_group, target_group, 7, 1)
        self.x = 0
        self.y = -1

    def update(self):
        super().update()
        if self.flag:
            if self.current_frame == len(self.frames) - 1:
                self.current_frame = -1
                self.flag = False
            
            self.current_frame += 1

            if self.current_frame == 2:
                bullet = Auto_Cannon_Bullet(self.rect.x + 15, self.rect.y + 24, self.target_group)
                self.bullet_group.add(bullet)
            
            elif self.current_frame == 3:
                bullet = Auto_Cannon_Bullet(self.rect.x + 33, self.rect.y + 24, self.target_group)
                self.bullet_group.add(bullet)

            self.image = self.frames[self.current_frame]


class Auto_Cannon_Bullet(Bullet):
    
    def __init__(self, x, y, target_group):
        super().__init__(x, y, (-1, 0), 'auto_cannon', characteristic['auto_cannon']['speed'], target_group, characteristic['auto_cannon']['damage'], 4, 1)


class Big_Space_Cannon(Player_Cannon):

    def __init__(self, bullet_group, target_group):
        super().__init__('big_space_cannon', bullet_group, target_group, 12, 1)
        self.x = 0
        self.y = -2

    def update(self):
        super().update()
        if self.flag:
            if self.current_frame == len(self.frames) - 1:
                self.current_frame = -1
                self.flag = False
            
            self.current_frame += 1

            if self.current_frame == 6:
                bullet = Big_Space_Cannon_Bullet(self.rect.x + 24, self.rect.y + 9, self.target_group)
                self.bullet_group.add(bullet)

            self.image = self.frames[self.current_frame]


class Big_Space_Cannon_Bullet(Bullet):
    
    def __init__(self, x, y, target_group):
        super().__init__(x, y, (-1, 0), 'big_space_cannon', characteristic['big_space_cannon']['speed'], target_group, characteristic['big_space_cannon']['damage'], 10, 1)