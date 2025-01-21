import pygame
import random
import animations
import get_settings
import math


characteristic = get_settings.characteristic()


class Game_Group(pygame.sprite.Group):
    
    def __init__(self, *sprites):
        self.groups = list()
        super().__init__(*sprites)

    def add(self, *groups):
        self.groups.extend(groups)

    def draw(self, surface):
        for group in self.groups:
            group.draw(surface)

    def update(self):
        for group in self.groups:
            group.update()


class Spaceship_Group(pygame.sprite.Group):
    pass


class Spaceship(pygame.sprite.Sprite):

    def __init__(self, x, y, wall, screen_width, screen_height, image, spaceship_group, bullet_group, target_group, hp, speed, shield_hp, shield_reload, shield_recover, shield_filename, shield_group, shield_x, shield_y, shield_columns, shield_rows):
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

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.hp = self.max_hp = hp
        self.speed = speed

        self.bullet_group = bullet_group
        self.target_group = target_group

        self.death_check = False

        self.shield = Shield(spaceship_group, shield_hp, shield_reload, shield_recover, shield_filename, shield_x, shield_y, shield_columns, shield_rows, shield_group, self)
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
                self.hp = 0
                self.death_check = True

    def check_move(self, x, y):
        return self.rect.x + x >= self.wall_x_min and self.rect.y + y >= self.wall_y_min and \
               self.rect.x + self.rect.width + x <= self.wall_x_max and \
               self.rect.y + self.rect.height + y <= self.wall_y_max 
    
    def update_health_bar(self):
        pass

    def death(self):
        self.shield.kill()
        self.kill()
    
    def update(self):
        self.shield.shield_update()


class Player_SpaceShip(Spaceship):
    
    def __init__(self, x, y, wall, screen_width, screen_height, spaceship_group, bullet_group, target_group, player_group, spaceship, cannon, cannon_name, engine, engine_name, health_bar_x, health_bar_y, health_bar_width, health_bar_height, health_bar_group):
        super().__init__(x, y, wall, screen_width, screen_height, characteristic[spaceship]['filename'][0], spaceship_group, bullet_group, target_group, characteristic[spaceship]['hp'], characteristic[spaceship]['speed'], characteristic[spaceship]['shield_hp'], characteristic[spaceship]['shield_reload'], characteristic[spaceship]['shield_recover'], characteristic[spaceship]['shield_filename'], player_group, characteristic[spaceship]['shield_x'], characteristic[spaceship]['shield_y'], characteristic[spaceship]['shield_columns'], characteristic[spaceship]['shield_rows'])
        self.stages = characteristic[spaceship]['filename']
        self.max_hp = self.hp

        self.engine = engine(characteristic[spaceship][engine_name + '_x'], characteristic[spaceship][engine_name + '_y'])
        self.engine.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)

        self.cannon = cannon(bullet_group, target_group, characteristic[spaceship][cannon_name + '_x'], characteristic[spaceship][cannon_name + '_y'], screen_width, screen_height)
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

        if 1 >= self.hp / self.max_hp > 0.75:
            self.image = pygame.image.load(self.stages[0])

        if 0.75 >= self.hp / self.max_hp > 0.5:
            self.image = pygame.image.load(self.stages[1])

        elif 0.5 >= self.hp / self.max_hp > 0.25:
            self.image = pygame.image.load(self.stages[2])

        elif 0.25 >= self.hp / self.max_hp:
            self.image = pygame.image.load(self.stages[3])

        self.update_health_bar()

    def update_health_bar(self):
        self.health_bar.update_health(self.hp)
        self.shield_bar.update_health(self.shield.hp)
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

    def __init__(self, spaceship_group, hp, reload, recover, filename, x, y, columns, rows, group, mothership):
        super().__init__()

        self.frames = animations.make_frames(filename, columns, rows)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())

        self.hp = self.max_hp = hp
        self.reload = reload
        self.recover = recover
        self.wait = 0

        self.x = x
        self.y = y

        self.group = group
        spaceship_group.add(self)
        self.mothership = mothership

    def hurt(self, damage):
        if self.hp > 0:
            self.wait = 0
            self.hp -= damage
            if self.hp < 0: self.hp = 0
            self.mothership.update_health_bar()
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

    def __init__(self, bullet_group, target_group, x, y, screen_width, screen_height):
        super().__init__('auto_cannon', bullet_group, target_group, 7, 1)
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self):
        super().update()

        if self.current_frame == 12:
            bullet = Auto_Cannon_Bullet(self.rect.x + 15, self.rect.y + 24, (0, -1), self.target_group, self.screen_width, self.screen_height)
            self.bullet_group.add(bullet)
        
        elif self.current_frame == 16:
            bullet = Auto_Cannon_Bullet(self.rect.x + 33, self.rect.y + 24, (0, -1), self.target_group, self.screen_width, self.screen_height)
            self.bullet_group.add(bullet)


class Big_Space_Cannon(Player_Cannon):

    def __init__(self, bullet_group, target_group, x, y, screen_width, screen_height):
        super().__init__('big_space_cannon', bullet_group, target_group, 12, 1)
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self):
        super().update()

        if self.current_frame == 28:
            bullet = Big_Space_Cannon_Bullet(self.rect.x + 24, self.rect.y + 9, (0, -1), self.target_group, self.screen_width, self.screen_height)
            self.bullet_group.add(bullet)


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction, cannon_name, target_group, screen_width, screen_height, columns=None, rows=None):
        super().__init__()
        if columns is None: columns = characteristic[cannon_name]['columns']
        if rows is None: rows = characteristic[cannon_name]['rows']

        self.damage = characteristic[cannon_name]['damage']
        self.direction = direction
        self.speed = characteristic[cannon_name]['bullet_speed']
        self.target_group = target_group

        self.angle = self.get_angle()
        
        self.frames = animations.make_frames(characteristic[cannon_name]['bullet_filename'], columns, rows)
        self.current_frame = 0
        self.image = pygame.transform.rotate(self.frames[self.current_frame], self.angle)
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())

        self.rect.x = self.x = x - self.rect.width // 2
        self.rect.y = self.y = y - self.rect.height // 2

        self.screen_height = screen_height
        self.screen_widht = screen_width


    def get_angle(self, vector1=None, vector2=(0, -1)):
        if vector1 is None:
            vector1 = self.direction
        ma = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
        mb = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)
        sc = vector1[0] * vector2[0] + vector1[1] * vector2[1]
        return math.degrees(math.acos(sc / ma / mb))
    
    def update(self):
        self.x += self.speed * self.direction[0]
        self.y += self.speed * self.direction[1]

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.image = pygame.transform.rotate(self.frames[self.current_frame], self.angle)

        if self.rect.x + self.rect.width < 0 or\
           self.rect.y + self.rect.height < 0 or\
           self.rect.x > self.screen_widht or\
           self.rect.y > self.screen_height:
            # self.kill()
            pass
        
        for sprite in self.target_group.sprites():
            for group in sprite.groups():
                if type(group) == Spaceship_Group: 
                    if pygame.sprite.collide_mask(self, sprite):
                        sprite.hurt(self.damage)
                        self.kill()
                        return


class Auto_Cannon_Bullet(Bullet):
    
    def __init__(self, x, y, direction, target_group, screen_width, screen_height):
        super().__init__(x, y, direction, 'auto_cannon', target_group, screen_width, screen_height, 4, 1)


class Big_Space_Cannon_Bullet(Bullet):
    
    def __init__(self, x, y, direction, target_group, screen_width, screen_height):
        super().__init__(x, y, direction, 'big_space_cannon', target_group, screen_width, screen_height, 10, 1)


class Enemy_Bullet(Bullet):
    def __init__(self, x, y, direction, target_group, screen_width, screen_height):
        super().__init__(x, y, direction, 'enemy_bullet', target_group, screen_width, screen_height)


class Enemy_Wave_Bullet(Bullet):
    
    def __init__(self, x, y, direction, target_group, screen_width, screen_height):
        super().__init__(x, y, direction, 'enemy_wave_bullet', target_group, screen_width, screen_height)


class Rocket(Bullet):

    def __init__(self, x, y, direction, cannon_name, target_group, screen_width, screen_height):
        super().__init__(x, y, direction, cannon_name, target_group, screen_width, screen_height)
        self.critical_angle = characteristic[cannon_name]['critical_angle']
        self.turn_angle = characteristic[cannon_name]['turn_angle']

    def turn(self, angle):
        self.direction = (math.sin(math.radians(angle)), math.cos(math.radians(angle)))

    def update(self):
        targets = []
        for sprite in self.target_group.sprites():
            for group in sprite.groups():
                if type(group) == Spaceship_Group: 
                    vector = (sprite.rect.x + sprite.rect.width // 2) - (self.rect.x + self.rect.width // 2), (sprite.rect.y + sprite.rect.height // 2) - (self.rect.y + self.rect.height // 2)
                    angle1 = self.get_angle()
                    angle2 = self.get_angle(vector1=vector)
                    if self.direction[0] < 0: angle1 = 360 - angle1
                    if vector[0] < 0: angle2 = 360 - angle2
                    angle = angle1 - angle2

                    if abs(angle) <= self.critical_angle:
                        targets.append((angle, abs(((self.rect.x + self.rect.width // 2) - (sprite.rect.x + sprite.rect.width // 2)) ** 2 + ((self.rect.y + self.rect.height // 2) - (sprite.rect.y + sprite.rect.height // 2) ** 2)) ** 0.5))

        if len(targets) != 0:
            turn_angle = min(targets, key=lambda x: x[1])[0]

            if abs(turn_angle) > self.turn_angle:
                if turn_angle < 0: turn_angle = -self.turn_angle
                elif turn_angle > 0: turn_angle = self.turn_angle

            self.turn(self.angle + turn_angle - 180)
            self.angle = self.angle + turn_angle

        super().update()


class Enemy_Rocket(Rocket):

    def __init__(self, x, y, direction, target_group, screen_width, screen_height):
        super().__init__(x, y, direction, 'enemy_rocket', target_group, screen_width, screen_height)


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

    def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, enemy_name, screen_width, screen_height):
        super().__init__(x, y, wall, screen_width, screen_height, characteristic[enemy_name]['filename'], spaceship_group, bullet_group, target_group, characteristic[enemy_name]['hp'], characteristic[enemy_name]['speed'], characteristic[enemy_name]['shield_hp'], characteristic[enemy_name]['shield_reload'], characteristic[enemy_name]['shield_recover'], characteristic[enemy_name]['shield_filename'], current_group, characteristic[enemy_name]['shield_x'], characteristic[enemy_name]['shield_y'], characteristic[enemy_name]['shield_columns'], characteristic[enemy_name]['shield_rows'])
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
                self.death()

            else:
                self.image = self.death_frames[self.death_current_frame]
                self.image = pygame.transform.rotate(self.image, 180)
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

            self.image = pygame.transform.rotate(self.image, 180)
            self.shield.image = pygame.transform.rotate(self.shield.image, 180)

            self.shoot()


class Enemy_Fighter(Enemy):
    
    def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, screen_width, screen_height):
        super().__init__(x, y, wall, spaceship_group, bullet_group, target_group, current_group, 'enemy_fighter', screen_width, screen_height)

    def update(self):
        super().update()

        if self.fire_current_frame == 8:
            bullet = Enemy_Bullet(self.rect.x + 23, self.rect.y + 43, (0, 1), self.target_group, self.screen_width, self.screen_height)
            self.bullet_group.add(bullet)

        elif self.fire_current_frame == 24:
            bullet = Enemy_Bullet(self.rect.x + 40, self.rect.y + 43, (0, 1), self.target_group, self.screen_width, self.screen_height)
            self.bullet_group.add(bullet)


class Enemy_Frigate(Enemy):

    def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, screen_width, screen_height):
        super().__init__(x, y, wall, spaceship_group, bullet_group, target_group, current_group, 'enemy_frigate', screen_width, screen_height)

    def update(self):
        super().update()

        if self.fire_current_frame == 24:
            bullet = Enemy_Wave_Bullet(self.rect.x + 32, self.rect.y + 42, (0, 1), self.target_group, self.screen_width, self.screen_height)
            self.bullet_group.add(bullet)


class Enemy_Torpedo(Enemy):
       
    def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, screen_width, screen_height):
        super().__init__(x, y, wall, spaceship_group, bullet_group, target_group, current_group, 'enemy_torpedo', screen_width, screen_height)

    def update(self):
        super().update()

        if self.fire_current_frame == 16:
            bullet = Enemy_Rocket(self.rect.x + 35, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
            self.bullet_group.add(bullet)

        if self.fire_current_frame == 24:
            bullet = Enemy_Rocket(self.rect.x + 29, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
            self.bullet_group.add(bullet)

        if self.fire_current_frame == 32:
            bullet = Enemy_Rocket(self.rect.x + 40, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
            self.bullet_group.add(bullet)

        if self.fire_current_frame == 40:
            bullet = Enemy_Rocket(self.rect.x + 24, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
            self.bullet_group.add(bullet)

        if self.fire_current_frame == 52:
            bullet = Enemy_Rocket(self.rect.x + 45, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
            self.bullet_group.add(bullet)

        if self.fire_current_frame == 60:
            bullet = Enemy_Rocket(self.rect.x + 19, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
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
