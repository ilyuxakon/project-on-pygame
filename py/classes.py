import pygame
import random
import animations
import get_settings

characteristic = get_settings.characteristic()

class Spaceship(pygame.sprite.Sprite):

    def __init__(self, x, y, wall, image, bullet_group, target_group, hp, speed, shield_hp, shield_reload, shield_recover, shield_filename, shield_group, shield_x, shield_y, shield_columns, shield_rows):
        super().__init__()
        self.image = pygame.image.load(image)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

        self.wall_x_min = wall[0]
        self.wall_y_min = wall[1]
        self.wall_x_max = wall[2]
        self.wall_y_max = wall[3]

        self.rect.x = x - self.rect.width // 2
        self.rect.y = y - self.rect.height // 2
                
        self.hp = self.max_hp = hp
        self.speed = speed

        self.bullet_group = bullet_group
        self.target_group = target_group

        self.death_check = False

        self.shield = Shield(shield_hp, shield_reload, shield_recover, shield_filename, shield_x, shield_y, shield_columns, shield_rows, shield_group)
        self.shield.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)

    def move(self, x, y):
        x = self.speed * x
        y = self.speed * y
        if self.check_move(x, y):
            self.rect.x += x
            self.rect.y += y
            self.shield.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)

    def hurt(self, damage):
        check = self.shield.hurt(damage)
        if check:
            self.hp -= damage
            if self.hp <= 0:
                self.death_check = True

    def check_move(self, x, y):
        return self.rect.x + x >= self.wall_x_min and self.rect.y + y >= self.wall_y_min and \
               self.rect.x + self.rect.width + x <= self.wall_x_max and \
               self.rect.y + self.rect.height + y <= self.wall_y_max 
    
    def update(self):
        self.shield.update()


class Player_SpaceShip(Spaceship):
    
    def __init__(self, x, y, wall, bullet_group, target_group, player_group, spaceship, cannon, cannon_name, engine, engine_name):
        super().__init__(x, y, wall, characteristic[spaceship]['filename'][0], bullet_group, target_group, characteristic[spaceship]['hp'], characteristic[spaceship]['speed'], characteristic[spaceship]['shield_hp'], characteristic[spaceship]['shield_reload'], characteristic[spaceship]['shield_recover'], characteristic[spaceship]['shield_filename'], player_group, 0, 0, 10, 1)
        self.stages = characteristic[spaceship]['filename'][1:]
        self.max_hp = self.hp

        self.engine = engine(characteristic[spaceship][engine_name + '_x'], characteristic[spaceship][engine_name + '_y'])
        self.engine.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)
        player_group.add(self.engine)

        self.cannon = cannon(bullet_group, target_group, characteristic[spaceship][cannon_name + '_x'], characteristic[spaceship][cannon_name + '_y'])
        self.cannon.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)
        player_group.add(self.cannon)

        player_group.add(self)
        player_group.add(self.shield)

    def shoot(self):
        self.cannon.shoot()

    def hurt(self, damage):
        super().hurt(damage)

        if 0.75 >= self.hp / self.max_hp > 0.5:
            self.image = pygame.image.load(self.stages[0])

        elif 0.5 >= self.hp / self.max_hp > 0.25:
            self.image = pygame.image.load(self.stages[1])

        elif 0.25 >= self.hp / self.max_hp:
            self.image = pygame.image.load(self.stages[2])

    def move(self, x, y):
        super().move(x, y)
        self.cannon.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)
        self.engine.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)


class Shield(pygame.sprite.Sprite):

    def __init__(self, hp, reload, recover, filename, x, y, columns, rows, group):
        super().__init__()

        self.frames = animations.make_frames(filename, columns, rows)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())

        self.hp = self.max_hp = hp
        self.reload = reload
        self.recover = recover
        self.wait = 0

        self.x = x
        self.y = y

        self.group = group

    def hurt(self, damage):
        if self.hp > 0:
            self.wait = 0
            self.hp -= damage
            if self.hp < 0: self.hp = 0
            return False

        else:
            return True            
    
    def move(self, x, y):
        self.rect.x = x - self.rect.width // 2 + self.x
        self.rect.y = y - self.rect.height // 2 + self.y

    def update(self):
        if self.hp != self.max_hp:
            self.wait += 1

        if self.hp != 0:
            if self.wait == 300 :
                self.hp += self.recover
                self.wait = 0

                if self.hp > self.max_hp: self.hp = self.max_hp

            if self.current_frame == len(self.frames) - 1:
                self.current_frame = -1

            self.current_frame += 1
            self.image = self.frames[self.current_frame]

        else:
            self.current_frame = -1
            self.group.remove(self)

            if self.wait == self.reload:
                self.hp = self.max_hp
                self.wait = 0
                self.group.add(self)
            

class Player_Cannon(pygame.sprite.Sprite):

    def __init__(self, cannon_name, bullet_group, target_group, columns, rows):
        super().__init__()

        self.frames = animations.make_frames(characteristic[cannon_name]['filename'], columns, rows)
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


class Auto_Cannon(Player_Cannon):

    def __init__(self, bullet_group, target_group, x, y):
        super().__init__('auto_cannon', bullet_group, target_group, 7, 1)
        self.x = x
        self.y = y

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


class Big_Space_Cannon(Player_Cannon):

    def __init__(self, bullet_group, target_group, x, y):
        super().__init__('big_space_cannon', bullet_group, target_group, 12, 1)
        self.x = x
        self.y = y

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


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction, cannon_name, target_group, columns, rows):
        super().__init__()
        self.frames = animations.make_frames(characteristic[cannon_name]['bullet_filename'], columns, rows)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        
        self.rect.x = x - self.rect.width // 2
        self.rect.y = y - self.rect.height // 2
        
        self.damage = characteristic[cannon_name]['damage']
        self.direction = direction
        self.speed = characteristic[cannon_name]['speed']
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


class Auto_Cannon_Bullet(Bullet):
    
    def __init__(self, x, y, target_group):
        super().__init__(x, y, (-1, 0), 'auto_cannon', target_group, 4, 1)


class Big_Space_Cannon_Bullet(Bullet):
    
    def __init__(self, x, y, target_group):
        super().__init__(x, y, (-1, 0), 'big_space_cannon', target_group, 10, 1)


class Engine(pygame.sprite.Sprite):

    def __init__(self, engine, idle_columns, idle_rows, powering_columns, powering_rows):
        super().__init__()
        self.engine = pygame.image.load(characteristic[engine]['engine_filename'])
        self.rect = self.engine.get_rect()

        self.idle_frames = animations.make_frames(characteristic[engine]['idle_filename'], idle_columns, idle_rows)
        self.idle_current_frame = 0
        self.idle_image = self.idle_frames[self.idle_current_frame]

        self.powering_frames = animations.make_frames(characteristic[engine]['powering_filename'], powering_columns, powering_rows)
        self.powering_current_frame = -1
        self.powering_image = self.powering_frames[self.powering_current_frame]

        self.image = self.idle_image
        self.image.blit(self.engine, (0, 0))

        self.work = False

    def move(self, x, y):
        self.rect.x = x - self.rect.width // 2 + self.x
        self.rect.y = y - self.rect.height // 2 + self.y
        self.work = True
    
    def update(self):
        if self.work:
            if self.powering_current_frame == len(self.powering_frames) - 1:
                self.powering_current_frame = -1

            self.powering_current_frame += 1
            self.powering_image = self.powering_frames[self.powering_current_frame]
            
            self.image = self.powering_image
            self.image.blit(self.engine, (0, 0))

            self.idle_current_frame = -1
            self.idle_image = self.powering_frames[self.powering_current_frame]

        else:
            if self.idle_current_frame == len(self.idle_frames) - 1:
                self.idle_current_frame = -1

            self.idle_current_frame += 1
            self.idle_image = self.idle_frames[self.idle_current_frame]

            self.image = self.idle_image
            self.image.blit(self.engine, (0, 0))

            self.powering_current_frame = -1
            self.powering_image = self.powering_frames[self.powering_current_frame]

        self.work = False


class Base_Engine(Engine):

    def __init__(self, x, y):
        super().__init__('base_engine', 3, 1, 4, 1)
        self.x = x
        self.y = y


class Enemy(Spaceship):

    def __init__(self, x, y, wall, enemy_name, bullet_group, target_group):
        super().__init__(x, y, wall, characteristic[enemy_name], bullet_group, target_group, characteristic[enemy_name]['hp'], characteristic[enemy_name]['speed'])
        self.reload = characteristic[enemy_name]['reload']
        self.current_reload = self.reload
        self.wait = 0

    def shoot(self):
        if self.wait > self.current_reload:
            self.wait = 0
            inaccuracy = random.randrange(-5, 6)
            self.current_reload = self.reload + (self.reload * inaccuracy * 0.1)
            self.flag = True

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.wait += 1
        self.shoot()