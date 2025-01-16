import pygame
import random
import animations
import get_settings
import math


characteristic = get_settings.characteristic()


class Spaceship_Group(pygame.sprite.Group):
    pass


class Spaceship(pygame.sprite.Sprite):

    def __init__(self, x, y, wall, image, spaceship_group, bullet_group, target_group, hp, speed, shield_hp, shield_reload, shield_recover, shield_filename, shield_group, shield_x, shield_y, shield_columns, shield_rows):
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

        spaceship_group.add(self)

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
        self.shield.shield_update()


class Player_SpaceShip(Spaceship):
    
    def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, player_group, spaceship, cannon, cannon_name, engine, engine_name, health_bar_x, health_bar_y, health_bar_width, health_bar_height, health_bar_group):
        super().__init__(x, y, wall, characteristic[spaceship]['filename'][0], spaceship_group, bullet_group, target_group, characteristic[spaceship]['hp'], characteristic[spaceship]['speed'], characteristic[spaceship]['shield_hp'], characteristic[spaceship]['shield_reload'], characteristic[spaceship]['shield_recover'], characteristic[spaceship]['shield_filename'], player_group, characteristic[spaceship]['shield_x'], characteristic[spaceship]['shield_y'], characteristic[spaceship]['shield_columns'], characteristic[spaceship]['shield_rows'])
        self.stages = characteristic[spaceship]['filename']
        self.max_hp = self.hp

        self.engine = engine(characteristic[spaceship][engine_name + '_x'], characteristic[spaceship][engine_name + '_y'])
        self.engine.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)

        self.cannon = cannon(bullet_group, target_group, characteristic[spaceship][cannon_name + '_x'], characteristic[spaceship][cannon_name + '_y'])
        self.cannon.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)
        
        player_group.add(self.engine)
        player_group.add(self.cannon)
        player_group.add(self)
        player_group.add(self.shield)

        self.health_bar = Health_Bar(health_bar_x, health_bar_y, health_bar_width, health_bar_height, None, pygame.color.Color('red'), self.hp, health_bar_group)
        self.shield_bar = Health_Bar(health_bar_x, health_bar_y + health_bar_height + 20, health_bar_width, health_bar_height, None, pygame.color.Color('blue'), self.shield.hp, health_bar_group)

    def shoot(self):
        self.cannon.shoot()

    def hurt(self, damage):
        super().hurt(damage)
        
        self.health_bar.update_health(self.hp)
        self.shield_bar.update_health(self.shield.hp)

        if 1 >= self.hp / self.max_hp > 0.75:
            self.image = pygame.image.load(self.stages[0])

        if 0.75 >= self.hp / self.max_hp > 0.5:
            self.image = pygame.image.load(self.stages[1])

        elif 0.5 >= self.hp / self.max_hp > 0.25:
            self.image = pygame.image.load(self.stages[2])

        elif 0.25 >= self.hp / self.max_hp:
            self.image = pygame.image.load(self.stages[3])

        if self.shield.hp == 0 and self.shield.wait == 0:
            self.shield_bar.healing(self.shield.max_hp, self.shield.reload)

    def move(self, x, y):
        super().move(x, y)
        self.cannon.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)
        self.engine.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)

    def update(self):
        if self.shield.hp != self.shield.max_hp and self.shield.wait == 0 and self.shield.hp != 0:
            if self.shield.max_hp - self.shield.hp < self.shield.recover:
                recover = self.shield.max_hp - self.shield.hp

            else: recover = self.shield.recover

            self.shield_bar.healing(recover, 180)

        super().update()
        self.health_bar.update_health(self.hp)
        self.shield_bar.update_health(self.shield.hp)


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

    def shield_update(self):
        if self.hp != self.max_hp:
            self.wait += 1

        if self.hp != 0:
            if self.wait == 180:
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

        self.frames = animations.make_frames(characteristic[cannon_name]['filename'], columns, rows, cannon=True)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.flag = False

        self.bullet_group = bullet_group
        self.target_group = target_group
        self.reload = self.current_reload = characteristic[cannon_name]['reload']
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

        if self.flag:
            if self.current_frame == len(self.frames) - 1:
                self.current_frame = -1
                self.flag = False
                self.wait = 0
            
            self.current_frame += 1
            self.image = self.frames[self.current_frame]


class Auto_Cannon(Player_Cannon):

    def __init__(self, bullet_group, target_group, x, y):
        super().__init__('auto_cannon', bullet_group, target_group, 7, 1)
        self.x = x
        self.y = y

    def update(self):
        super().update()

        if self.current_frame == 3:
            bullet = Auto_Cannon_Bullet(self.rect.x + 15, self.rect.y + 24, (0, -1), self.target_group)
            self.bullet_group.add(bullet)
        
        elif self.current_frame == 4:
            bullet = Auto_Cannon_Bullet(self.rect.x + 33, self.rect.y + 24, (0, -1), self.target_group)
            self.bullet_group.add(bullet)


class Big_Space_Cannon(Player_Cannon):

    def __init__(self, bullet_group, target_group, x, y):
        super().__init__('big_space_cannon', bullet_group, target_group, 12, 1)
        self.x = x
        self.y = y

    def update(self):
        super().update()

        if self.current_frame == 7:
            bullet = Big_Space_Cannon_Bullet(self.rect.x + 24, self.rect.y + 9, (0, -1), self.target_group)
            self.bullet_group.add(bullet)


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction, cannon_name, target_group, columns, rows):
        super().__init__()
        
        self.damage = characteristic[cannon_name]['damage']
        self.direction = direction
        self.speed = characteristic[cannon_name]['bullet_speed']
        self.target_group = target_group

        self.get_angle()
        
        self.frames = animations.make_frames(characteristic[cannon_name]['bullet_filename'], columns, rows)
        self.current_frame = 0
        self.image = pygame.transform.rotate(self.frames[self.current_frame], self.angle)
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())

        self.rect.x = x - self.rect.width // 2
        self.rect.y = y - self.rect.height // 2

    def get_angle(self):
        self.angle = math.degrees(math.atan2(0 - (-1 * self.direction[0]), 0 + (-1 * self.direction[1])))

    def update(self):
        self.rect.x += self.speed * self.direction[0]
        self.rect.y += self.speed * self.direction[1]

        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.image = pygame.transform.rotate(self.frames[self.current_frame], self.angle)

        if self.rect.x + self.rect.width < -100 or\
           self.rect.y + self.rect.height < -100 or\
           self.rect.x > 4100 or\
           self.rect.y > 4100:
            self.kill()
        
        for sprite in self.target_group.sprites():
            for group in sprite.groups():
                if type(group) == Spaceship_Group: 
                    if pygame.sprite.collide_mask(self, sprite):
                        sprite.hurt(self.damage)
                        self.kill()
                        break


class Auto_Cannon_Bullet(Bullet):
    
    def __init__(self, x, y, direction, target_group):
        super().__init__(x, y, direction, 'auto_cannon', target_group, 4, 1)


class Big_Space_Cannon_Bullet(Bullet):
    
    def __init__(self, x, y, direction, target_group):
        super().__init__(x, y, direction, 'big_space_cannon', target_group, 10, 1)


class Fighter_Bullet(Bullet):
    def __init__(self, x, y, direction, target_group):
        super().__init__(x, y, direction, 'enemy_fighter', target_group, 8, 1)


class Engine(pygame.sprite.Sprite):

    def __init__(self, engine, idle_columns, idle_rows, powering_columns, powering_rows):
        super().__init__()
        self.engine = pygame.image.load(characteristic[engine]['engine_filename'])
        self.rect = self.engine.get_rect()

        self.idle_frames = animations.make_frames(characteristic[engine]['idle_filename'], idle_columns, idle_rows)
        self.idle_current_frame = 0
        self.idle_image = self.idle_frames[self.idle_current_frame].copy()

        self.powering_frames = animations.make_frames(characteristic[engine]['powering_filename'], powering_columns, powering_rows)
        self.powering_current_frame = -1
        self.powering_image = self.powering_frames[self.powering_current_frame].copy()
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
            self.powering_image = self.powering_frames[self.powering_current_frame].copy()
            
            self.image = self.powering_image
            self.image.blit(self.engine, (0, 0))

            self.idle_current_frame = -1
            self.idle_image = self.powering_frames[self.powering_current_frame]

        else:
            if self.idle_current_frame == len(self.idle_frames) - 1:
                self.idle_current_frame = -1

            self.idle_current_frame += 1
            self.idle_image = self.idle_frames[self.idle_current_frame].copy()

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

    def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, enemy_name):
        super().__init__(x, y, wall, characteristic[enemy_name]['filename'], spaceship_group, bullet_group, target_group, characteristic[enemy_name]['hp'], characteristic[enemy_name]['speed'], characteristic[enemy_name]['shield_hp'], characteristic[enemy_name]['shield_reload'], characteristic[enemy_name]['shield_recover'], characteristic[enemy_name]['shield_filename'], current_group, characteristic[enemy_name]['shield_x'], characteristic[enemy_name]['shield_y'], characteristic[enemy_name]['shield_columns'], characteristic[enemy_name]['shield_rows'])
        self.spaceship = pygame.image.load(characteristic[enemy_name]['filename'])

        self.current_group = current_group

        self.reload = self.current_reload =characteristic[enemy_name]['reload']
        self.wait = -1

        self.engine_frames = animations.make_frames(characteristic[enemy_name]['engine_filename'], characteristic[enemy_name]['engine_columns'], characteristic[enemy_name]['engine_rows'])
        self.engine_current_frame = -1

        self.fire_frames = animations.make_frames(characteristic[enemy_name]['fire_filename'], characteristic[enemy_name]['fire_columns'], characteristic[enemy_name]['fire_rows'], cannon=True)
        self.fire_current_frame = -1
        self.fire_flag = False

        self.death_frames = animations.make_frames(characteristic[enemy_name]['death_filename'], characteristic[enemy_name]['death_columns'], characteristic[enemy_name]['death_rows'])
        self.death_current_frame = 0

        self.current_group.add(self)
        self.current_group.add(self.shield)

        self.update()
    
    def shoot(self):
        if self.wait >= self.current_reload:
            self.wait = 0
            inaccuracy = random.randrange(-5, 6)
            self.current_reload = self.reload + (self.reload * inaccuracy * 0.1)
            self.fire_flag = True

    def update(self):
        if self.death_check:
            if self.death_current_frame == len(self.death_frames):
                self.kill()

            else:
                self.image = self.death_frames[self.death_current_frame]
                self.image = pygame.transform.flip(self.image, False, True)
                self.death_current_frame += 1

        else:
            super().update()
            self.wait += 1
            
            if self.fire_flag:
                if self.fire_current_frame == len(self.fire_frames) - 1:
                    self.fire_current_frame = -1
                    self.fire_flag = False
                    self.wait = 0

                self.fire_current_frame += 1
                self.image = self.fire_frames[self.fire_current_frame].copy()

            else:
                self.image = self.spaceship.copy()

            if self.engine_current_frame == len(self.engine_frames) - 1:
                self.engine_current_frame = -1

            self.engine_current_frame += 1
            self.engine_image = self.engine_frames[self.engine_current_frame]
            self.image.blit(self.engine_image, (0, 0))

            self.image = pygame.transform.flip(self.image, False, True)
            self.shield.image = pygame.transform.flip(self.shield.image, False, True)

            self.shoot()


class Enemy_Fighter(Enemy):
    
    def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group):
        super().__init__(x, y, wall, spaceship_group, bullet_group, target_group, current_group, 'enemy_fighter')

    def update(self):
        super().update()

        if self.fire_current_frame == 2:
            bullet = Fighter_Bullet(self.rect.x + 23, self.rect.y + 43, (0, 1), self.target_group)
            self.bullet_group.add(bullet)

        elif self.fire_current_frame == 6:
            bullet = Fighter_Bullet(self.rect.x + 40, self.rect.y + 43, (0, 1), self.target_group)
            self.bullet_group.add(bullet)


class Wall(pygame.sprite.Sprite):

    def __init__(self, x, start_y, end_y, group):
        super().__init__()
        self.image = pygame.surface.Surface((4, end_y - start_y))
        self.image.fill(pygame.color.Color('white'))
        self.rect = self.image.get_rect()
        self.rect.x = x
        group.add(self)


class Health_Bar(pygame.sprite.Sprite):

    def __init__(self, x, y, width, height, image, color, hp, group):
        super().__init__()
        self.originall_image = pygame.surface.Surface((width, height))
        self.rect = self.originall_image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.color = color

        self.hp = self.max_hp =  hp
        self.pixel = width / hp
        self.wait = 0
        self.frames = 1
        self.healing_flag = False

        self.update_health(hp)
        group.add(self)

    def update_health(self, hp):
        if self.hp != hp:
            self.stop_healing()

        self.hp = hp
        self.image = self.originall_image.copy()
        width = int(self.hp * self.pixel)
        pygame.draw.rect(self.image, self.color, (0, 0, width, self.rect.height))

        if self.healing_flag:
            self.wait += 1
            rect = pygame.surface.Surface((int(self.wait * self.step), self.rect.height))
            rect.set_alpha(50)
            rect.fill(self.color)
            self.image.blit(rect, (int(self.hp * self.pixel), 0))

        text = str(self.hp) + '/' + str(self.max_hp)
        font = pygame.font.Font(None, self.rect.height)
        text = font.render(text, True, pygame.color.Color('white'))
        self.image.blit(text, ((self.rect.width - text.get_width()) // 2, (self.rect.height - text.get_height()) // 2))

        if self.wait > self.frames:
            self.stop_healing()
            self.update_health(self.hp + self.healing_hp)

    def healing(self, hp, frames):
        if self.hp + hp > self.max_hp: hp = self.max_hp - self.hp

        self.healing_flag = True
        self.step = (hp * self.pixel) / frames
        self.healing_hp = hp
        self.frames = frames

    def stop_healing(self):
        self.healing_flag = False
        self.wait = 0
    