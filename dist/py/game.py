import pygame
import random
import math
import get_settings
import animations


characteristic = get_settings.characteristic()


class Game_Group(pygame.sprite.Group):  # группа обрабатывающая другие группы
    
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


class Spaceship():
    
    class Spaceship_Group(pygame.sprite.Group):  # группа кораблей, нужна для выделения спрайтов с которыми взаимодействуют боеприпасы
        pass


    class Spaceship():
        
        class Spaceship(pygame.sprite.Sprite):  # базовый класс космического корабля

            def __init__(self, x, y, wall, screen_width, screen_height, image, spaceship_group, hp, speed):
                super().__init__()
                self.image = pygame.image.load(image)
                self.mask = pygame.mask.from_surface(self.image)
                self.rect = self.image.get_rect()

                # зона по которой корабль может передвигаться
                self.wall_x_min = wall[0]
                self.wall_y_min = wall[1]
                self.wall_x_max = wall[2]
                self.wall_y_max = wall[3]

                self.rect.x = self.x = x - self.rect.width // 2
                self.rect.y = self.y = y - self.rect.height // 2

                self.screen_width = screen_width
                self.screen_height = screen_height

                self.hp = self.max_hp = hp
                self.speed = speed

                self.death_check = False
                spaceship_group.add(self)


            def shield_move(self):  # заглушка
                pass


            def move(self, x, y):
                x = self.speed * x
                y = self.speed * y
                if self.check_move(x, y):
                    self.x += x
                    self.y += y
                    self.rect.x = int(self.x)
                    self.rect.y = int(self.y)
                    self.shield_move()
                    return -1
                
                else:  # если движение навозможно, возвращает ось по которой оно невозможно
                    if self.check_move(0, y):
                        return 0
                    if self.check_move(x, 0):
                        return 1
                    
                    return 2


            def hurt(self, damage):
                self.hp -= damage
                if self.hp <= 0:
                    sound = pygame.mixer.Sound('data\sound\explosion.mp3')
                    sound.set_volume(0.01)
                    sound.play()
                                
                    self.hp = 0
                    self.death_check = True
                    self.speed = 0


            def check_move(self, x, y):
                return self.x + x >= self.wall_x_min and self.y + y >= self.wall_y_min and \
                    self.x + self.rect.width + x <= self.wall_x_max and \
                    self.y + self.rect.height + y <= self.wall_y_max 


        class Battle_Spaceship(Spaceship):  # класс боевого космического корабля

            def __init__(self, x, y, wall, screen_width, screen_height, image, spaceship_group, bullet_group, target_group, hp, speed, shield_hp, shield_reload, shield_recover, shield_filename, shield_group, shield_x, shield_y, shield_columns, shield_rows):
                super().__init__(x, y, wall, screen_width, screen_height, image, spaceship_group, hp, speed)
                self.bullet_group = bullet_group
                self.target_group = target_group
                
                self.shield = Spaceship.Shield(spaceship_group, shield_hp, shield_reload, shield_recover, shield_filename, shield_x, shield_y, shield_columns, shield_rows, shield_group, self)
                self.shield.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)


            def shield_move(self):
                self.shield.move(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)


            def hurt(self, damage):
                check = self.shield.hurt(damage)
                if check:
                    return super().hurt(damage)


            def update_health_bar(self):  # заглушка
                pass


            def death(self):
                self.shield.kill()
                self.kill()


            def update(self):
                self.shield.shield_update()


        class Player_Spaceship(Battle_Spaceship):  # класс корабля игрока
            
            def __init__(self, x, y, wall, screen_width, screen_height, spaceship_group, bullet_group, target_group, player_group, spaceship, shield_name, cannon, cannon_name, engine, engine_name, health_bar_x, health_bar_y, health_bar_width, health_bar_height, health_bar_group):
                super().__init__(x, y, wall, screen_width, screen_height, characteristic[spaceship]['filename'][0], spaceship_group, bullet_group, target_group, characteristic[spaceship]['hp'], characteristic[spaceship]['speed'], characteristic[shield_name]['shield_hp'], characteristic[shield_name]['shield_reload'], characteristic[shield_name]['shield_recover'], characteristic[shield_name]['shield_filename'], player_group, characteristic[shield_name]['shield_x'], characteristic[shield_name]['shield_y'], characteristic[shield_name]['shield_columns'], characteristic[shield_name]['shield_rows'])
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
                
                self.health_bar = Other.Health_Bar(health_bar_x, health_bar_y, health_bar_width, health_bar_height, None, pygame.color.Color('red'), self.hp, health_bar_group)
                self.shield_bar = Other.Health_Bar(health_bar_x, health_bar_y + health_bar_height + 20, health_bar_width, health_bar_height, None, pygame.color.Color('blue'), self.shield.hp, health_bar_group)


            def shoot(self):
                self.cannon.shoot()


            def hurt(self, damage):
                super().hurt(damage)

                # меняет текстурку игрока в зависимости от степени повреждений
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
                
                if self.shield.hp == 0 and self.shield.wait == 0: # если щит полностью сломан, начинает его восстанавливать
                    self.shield_bar.healing(self.shield.max_hp, self.shield.reload)


            def move(self, x, y):
                if self.cannon.can_move:  # если игрок может двигаться (во время стрельбы орудие zapper не даёт игроку двигаться)
                    super().move(x, y)
                    self.cannon.move(self.rect.centerx, self.rect.centery)
                    self.engine.move(self.rect.centerx, self.rect.centery)
            
            
            def death(self):
                self.cannon.death()
                super().death()


            def update(self):
                # если щит повреждён и ещё не начал восстановление, начинает восстановление щита
                if self.shield.hp != self.shield.max_hp and self.shield.wait == 0 and self.shield.hp != 0:
                    if self.shield.max_hp - self.shield.hp < self.shield.recover:
                        recover = self.shield.max_hp - self.shield.hp

                    else: recover = self.shield.recover

                    self.shield_bar.healing(recover, 180)

                super().update()
                self.health_bar.update_health(self.hp)
                self.shield_bar.update_health(self.shield.hp)


        class Enemy(Battle_Spaceship):  # базовый класс врага

            def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, enemy_name, screen_width, screen_height):
                super().__init__(x, y, wall, screen_width, screen_height, characteristic[enemy_name]['filename'], spaceship_group, bullet_group, target_group, characteristic[enemy_name]['hp'], characteristic[enemy_name]['speed'], characteristic[enemy_name]['shield_hp'], characteristic[enemy_name]['shield_reload'], characteristic[enemy_name]['shield_recover'], characteristic[enemy_name]['shield_filename'], current_group, characteristic[enemy_name]['shield_x'], characteristic[enemy_name]['shield_y'], characteristic[enemy_name]['shield_columns'], characteristic[enemy_name]['shield_rows'])
                self.spaceship = pygame.image.load(characteristic[enemy_name]['filename'])

                self.current_group = current_group

                self.reload = characteristic[enemy_name]['reload']  # среднее время перезарядки
                inaccuracy = random.randrange(-5, 6)
                self.current_reload = self.reload + (self.reload * inaccuracy * 0.1)  # текущее время перезарядки с учётом погрешности
                self.wait = -1

                # анимация двигателей
                self.engine_frames = animations.make_frames(characteristic[enemy_name]['engine_filename'], characteristic[enemy_name]['engine_columns'], characteristic[enemy_name]['engine_rows'])
                self.engine_current_frame = -1

                # анимация стрельбы
                self.fire_frames = animations.make_frames(characteristic[enemy_name]['fire_filename'], characteristic[enemy_name]['fire_columns'], characteristic[enemy_name]['fire_rows'], cannon=True)
                self.fire_current_frame = -1
                self.fire_flag = False

                # анимация смерти
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


            def death(self):
                pygame.event.post(pygame.event.Event(pygame.USEREVENT))
                super().death()


            def update(self):
                if self.death_check:  # срабатывание анимации смерти
                    if self.death_current_frame == len(self.death_frames):
                        self.death()

                    else:
                        self.fire_current_frame =  0
                        self.image = self.death_frames[self.death_current_frame]
                        self.image = pygame.transform.rotate(self.image, 180)
                        self.death_current_frame += 1

                else:
                    super().update()
                    self.wait += 1  # перезарядка
                    
                    if self.fire_flag and self.fire_frames is not None: # срабатывание анимации стрельбы
                        if self.fire_current_frame == len(self.fire_frames) - 1:
                            self.fire_current_frame = -1
                            self.fire_flag = False
                            self.wait = 0

                        self.fire_current_frame += 1
                        self.image = self.fire_frames[self.fire_current_frame].copy()

                    else:
                        self.image = self.spaceship.copy()

                    # анимация двигателей
                    if self.engine_current_frame == len(self.engine_frames) - 1:
                        self.engine_current_frame = -1

                    self.engine_current_frame += 1
                    self.engine_image = self.engine_frames[self.engine_current_frame]

                    # финальное изображение
                    self.image.blit(self.engine_image, (0, 0))
                    self.image = pygame.transform.rotate(self.image, 180)
                    self.shield.image = pygame.transform.rotate(self.shield.image, 180)

                    self.shoot()


        class Enemy_Fighter(Enemy):
            
            def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, screen_width, screen_height):
                super().__init__(x, y, wall, spaceship_group, bullet_group, target_group, current_group, 'enemy_fighter', screen_width, screen_height)


            def update(self):
                super().update()

                if self.fire_current_frame == 8:  # синхронизирует анимацию стрельбы, звук, появление пули
                    sound = pygame.mixer.Sound('data\sound\weapon\\bullet.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                    bullet = Bullet.Enemy_Bullet(self.rect.x + 23, self.rect.y + 43, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)

                elif self.fire_current_frame == 24:  # синхронизирует анимацию стрельбы, звук, появление пули
                    sound = pygame.mixer.Sound('data\sound\weapon\\bullet.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                    bullet = Bullet.Enemy_Bullet(self.rect.x + 40, self.rect.y + 43, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)


        class Enemy_Frigate(Enemy):

            def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, screen_width, screen_height):
                super().__init__(x, y, wall, spaceship_group, bullet_group, target_group, current_group, 'enemy_frigate', screen_width, screen_height)


            def update(self):
                super().update()

                if self.fire_current_frame == 24:  # синхронизирует анимацию стрельбы, звук, появление пули
                    sound = pygame.mixer.Sound('data\sound\weapon\\wave.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                    bullet = Bullet.Enemy_Wave_Bullet(self.rect.x + 32, self.rect.y + 42, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)


        class Enemy_Torpedo(Enemy):
            
            def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, screen_width, screen_height):
                super().__init__(x, y, wall, spaceship_group, bullet_group, target_group, current_group, 'enemy_torpedo', screen_width, screen_height)


            def update(self):
                super().update()

                if self.fire_current_frame == 12:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                elif self.fire_current_frame == 16:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Enemy_Rocket(self.rect.x + 35, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)

                elif self.fire_current_frame == 20:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                elif self.fire_current_frame == 24:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Enemy_Rocket(self.rect.x + 29, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)

                elif self.fire_current_frame == 28:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                elif self.fire_current_frame == 32:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Enemy_Rocket(self.rect.x + 40, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)
                    
                elif self.fire_current_frame == 36:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()

                elif self.fire_current_frame == 40:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Enemy_Rocket(self.rect.x + 24, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)

                elif self.fire_current_frame == 48:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                elif self.fire_current_frame == 52:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Enemy_Rocket(self.rect.x + 45, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)
                
                elif self.fire_current_frame == 56:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()

                elif self.fire_current_frame == 60:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Enemy_Rocket(self.rect.x + 19, self.rect.y + 38, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)


        class Enemy_Scout(Enemy):

            def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, screen_width, screen_height):
                a = random.random()
                n1 = random.choice((-1, 1))
                n2 = random.choice((-1, 1))
                self.direction = [a * n1, (1 - a) * n2] # создаёт случайный вектор направления движение
                super().__init__(x, y, wall, spaceship_group, bullet_group, target_group, current_group, 'enemy_scout', screen_width, screen_height)


            def update(self):
                super().update()        

                # если движение по вектору невозможно, проверка по какой оси оно невозможно и разворачивает движение по этой оси на противоположное
                check = self.move(*self.direction) 
                if check == 0 or check == 2:
                    self.direction[0] *= -1

                if check == 1 or check == 2:
                    self.direction[1] *= -1

                if self.fire_current_frame == 8:  # синхронизирует анимацию стрельбы, звук, появление пули
                    sound = pygame.mixer.Sound('data\sound\weapon\\plasma.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                
                elif self.fire_current_frame == 12:  # синхронизирует анимацию стрельбы, звук, появление пули
                    bullet = Bullet.Enemy_Energy_Bullet(self.rect.x + 32, self.rect.y + 40, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)


        class Enemy_Bomber(Enemy):
            def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, screen_width, screen_height):
                self.direction = [random.choice((-1, 1)), 0] # выбирает направление движения
                super().__init__(x, y, wall, spaceship_group, bullet_group, target_group, current_group, 'enemy_bomber', screen_width, screen_height)


            def update(self):
                super().update()
                
                # если движение по невозможно, меняет движение на противоположное
                check = self.move(*self.direction)
                if check != -1:
                    self.direction[0] *= -1

                if self.fire_flag:  # синхронизирует анимацию стрельбы, появление бомбы
                    bullet = Bullet.Enemy_Bomb(self.rect.x + 32, self.rect.y + 42, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)
                    self.fire_flag = False
                    self.wait = 0


        class Enemy_Battlecruiser(Enemy):

            def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, screen_width, screen_height):
                super().__init__(x, y, wall, spaceship_group, bullet_group, target_group, current_group, 'enemy_battlecruiser', screen_width, screen_height)


            def update(self):
                super().update()

                if self.fire_current_frame == 4:  # синхронизирует анимацию стрельбы, звук, появление пули
                    sound = pygame.mixer.Sound('data\sound\weapon\\bullet.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                    bullet = Bullet.Enemy_Bullet(self.rect.x + 81, self.rect.y + 86, (0.15, 0.85), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)
                    
                elif self.fire_current_frame == 24:  # синхронизирует анимацию стрельбы, звук, появление пули
                    sound = pygame.mixer.Sound('data\sound\weapon\\plasma.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                    sound = pygame.mixer.Sound('data\sound\weapon\\bullet.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                    bullet = Bullet.Enemy_Bullet(self.rect.x + 47, self.rect.y + 86, (-0.15, 0.85), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)
                
                elif self.fire_current_frame == 28:  # синхронизирует анимацию стрельбы, звук, появление пули
                    
                    bullet = Bullet.Enemy_Energy_Bullet(self.rect.x + 78, self.rect.y + 105, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)

                    bullet = Bullet.Enemy_Energy_Bullet(self.rect.x + 50, self.rect.y + 105, (0, 1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)


        class Enemy_Dreadnought(Enemy):
                
                def __init__(self, x, y, wall, spaceship_group, bullet_group, target_group, current_group, screen_width, screen_height):
                    super().__init__(x, y, wall, spaceship_group, bullet_group, target_group, current_group, 'enemy_dreadnought', screen_width, screen_height)


                def update(self):
                    super().update()
                    
                    if self.death_check: # при смерти удаляет луч
                        self.ray.kill()
                        self.sound.stop()

                    if self.fire_current_frame == 68:  # синхронизирует анимацию стрельбы, звук, появление луча
                        self.sound = pygame.mixer.Sound('data\sound\weapon\\ray.mp3')
                        self.sound.set_volume(0.05)
                        self.sound.play()
                        
                        bullet = Bullet.Enemy_Ray(self.rect.x + 64, self.rect.y + 90, (0, 1), self.target_group, self.screen_width, self.screen_height)
                        self.ray = bullet
                        self.bullet_group.add(bullet)
                        
                    elif self.fire_current_frame == 124:  # по окончанию анимации стрельбы убирает луч и прекращает звук
                        self.ray.kill()
                        self.sound.stop()

                    flag = False

                    for sprite in self.target_group.sprites():
                        # ищет игрока и выбирает направление движения в его сторону
                        if type(sprite) == Spaceship.Spaceship.Player_Spaceship:
                            if self.rect.centerx > sprite.rect.centerx and abs(self.rect.centerx - sprite.rect.centerx) > 1:
                                direction = (-1, 0)
                                flag = True

                            elif self.rect.centerx < sprite.rect.centerx and abs(self.rect.centerx - sprite.rect.centerx) > 1:
                                direction = (1, 0)
                                flag = True

                            break
                    
                    if flag:
                        for sprite in self.current_group.sprites():
                            # не дайт двум дреноутам "входить" друг в друга
                            if type(sprite) == Spaceship.Spaceship.Enemy_Dreadnought and sprite != self:
                                self.move(*direction)
                                
                                if pygame.sprite.collide_mask(self.shield, sprite.shield):
                                    flag = False
                                    self.move(direction[0] * -1, direction[1] * -1)
                                    break
                                
                                self.move(direction[0] * -1, direction[1] * -1)
                        
                        if flag: self.move(*direction)  # если всё ок, двигается за игроком
                    
                    if 68 < self.fire_current_frame < 124: # при стрельбе двигает луч за дредноутом
                        self.ray.rect.centerx = self.rect.centerx
            
                
    class Shield(pygame.sprite.Sprite):

        def __init__(self, spaceship_group, hp, reload, recover, filename, x, y, columns, rows, group, mothership):
            super().__init__()

            self.frames = animations.make_frames(filename, columns, rows)
            self.current_frame = 0
            self.image = self.frames[self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())

            self.hp = self.max_hp = hp
            self.reload = reload  # время нужное для полной регенерации щита
            self.recover = recover  # прочность которую восстанавливает щит, если на протяжении 180 кадров (3 секунды) не получает урон
            self.wait = 0

            self.x = x
            self.y = y

            self.group = group
            spaceship_group.add(self)
            self.mothership = mothership


        def hurt(self, damage):
            # если ломается и не может поглощать урон возвращает True, иначе - False
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
            if self.hp != self.max_hp:  # если щит повреждён - увеличивает значение таймера
                self.wait += 1

            if self.hp != 0:  # если щит не сломан окончательно - проверяет таймер, восстанавливает щит, ставит следующий кадр
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
                self.group.remove(self) # если щит сломан, самоудаляет себя из группы, чтобы не отрисовываться и не поглощать выстрелы противника

                if self.wait == self.reload:
                    self.hp = self.max_hp
                    self.wait = 0
                    self.group.add(self) # если щит восстановлен, возвращает себя в группу
                
                
    class Cannon():
        
        class Player_Cannon(pygame.sprite.Sprite):  # базовый класс орудия игрока

            def __init__(self, cannon_name, bullet_group, target_group, columns, rows):
                super().__init__()

                self.frames = animations.make_frames(characteristic[cannon_name]['filename'], columns, rows, cannon=True)
                self.current_frame = 0
                self.image = self.frames[self.current_frame]
                self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
                self.flag = False

                self.bullet_group = bullet_group
                self.target_group = target_group
                self.reload = characteristic[cannon_name]['reload']  # среднее значение перезарядки
                inaccuracy = random.randrange(-5, 6)
                self.current_reload = self.reload + (self.reload * inaccuracy * 0.1)
                self.damage = characteristic[cannon_name]['damage']  # текущее значение перезарядки с учётом погрешности
                
                self.can_move = True
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


            def death(self):  # заглушка
                pass


            def update(self):
                self.wait += 1

                if self.flag:  # если орудие стреляет - ставит следующий кадр
                    if self.current_frame == len(self.frames) - 1:
                        self.current_frame = -1
                        self.flag = False
                        self.wait = 0
                    
                    self.current_frame += 1
                    self.image = self.frames[self.current_frame]


        class Auto_Cannon(Player_Cannon):

            def __init__(self, bullet_group, target_group, x, y, screen_width, screen_height):
                super().__init__('auto_cannon', bullet_group, target_group, 7, 1)
                
                self.x, self.y = x, y
                self.screen_width = screen_width
                self.screen_height = screen_height


            def update(self):
                super().update()

                if self.current_frame == 12:  # синхронизирует анимацию стрельбы, звук, появление пули
                    sound = pygame.mixer.Sound('data\sound\weapon\\bullet.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                    bullet = Bullet.Auto_Cannon_Bullet(self.rect.x + 15, self.rect.y + 24, (0, -1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)
                
                elif self.current_frame == 16:  # синхронизирует анимацию стрельбы, звук, появление пули
                    sound = pygame.mixer.Sound('data\sound\weapon\\bullet.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                    bullet = Bullet.Auto_Cannon_Bullet(self.rect.x + 33, self.rect.y + 24, (0, -1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)


        class Big_Space_Cannon(Player_Cannon):

            def __init__(self, bullet_group, target_group, x, y, screen_width, screen_height):
                super().__init__('big_space_cannon', bullet_group, target_group, 12, 1)
                
                self.x, self.y = x, y
                self.screen_width = screen_width
                self.screen_height = screen_height


            def update(self):
                super().update()

                if self.current_frame == 24:  # синхронизирует анимацию стрельбы, звук, появление пули
                    sound = pygame.mixer.Sound('data\sound\weapon\plasma.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                elif self.current_frame == 28:  # синхронизирует анимацию стрельбы, звук, появление пули
                    bullet = Bullet.Big_Space_Cannon_Bullet(self.rect.x + 24, self.rect.y + 9, (0, -1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)


        class Rockets_Cannon(Player_Cannon):

            def __init__(self, bullet_group, target_group, x, y, screen_width, screen_height):
                super().__init__('rockets_cannon', bullet_group, target_group, 17, 1)
                
                self.x, self.y = x, y
                self.screen_width = screen_width
                self.screen_height = screen_height


            def update(self):
                super().update()

                if self.current_frame == 4:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()

                elif self.current_frame == 8:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Player_Rocket(self.rect.x + 18, self.rect.y + 23, (0, -1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)

                elif self.current_frame == 12:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                elif self.current_frame == 16:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Player_Rocket(self.rect.x + 31, self.rect.y + 23, (0, -1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)

                elif self.current_frame == 20:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                elif self.current_frame == 24:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Player_Rocket(self.rect.x + 14, self.rect.y + 27, (0, -1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)
                
                elif self.current_frame == 28:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                elif self.current_frame == 32:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Player_Rocket(self.rect.x + 35, self.rect.y + 27, (0, -1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)
                
                elif self.current_frame == 46:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                elif self.current_frame == 40:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Player_Rocket(self.rect.x + 10, self.rect.y + 31, (0, -1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)

                elif self.current_frame == 44:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    sound = pygame.mixer.Sound('data\sound\weapon\\rocket.mp3')
                    sound.set_volume(0.05)
                    sound.play()
                    
                elif self.current_frame == 48:  # синхронизирует анимацию стрельбы, звук, появление ракеты
                    bullet = Bullet.Player_Rocket(self.rect.x + 39, self.rect.y + 31, (0, -1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet)
            

        class Zapper_Cannon(Player_Cannon):
            
            def __init__(self, bullet_group, target_group, x, y, screen_width, screen_height):
                super().__init__('zapper_cannon', bullet_group, target_group, 14, 1)

                self.x, self.y = x, y
                self.screen_width = screen_width
                self.screen_height = screen_height
            
            
            def death(self):  # убирает лучи и удаляет звук
                self.rays[0].kill()
                self.rays[1].kill()
                self.sound.stop()


            def update(self):
                super().update()

                if self.current_frame == 12:  # синхронизирует анимацию стрельбы, звук, появление луча
                    bullet1 = Bullet.Player_Ray(self.rect.x + 16, self.rect.y + 30, (0, -1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet1)

                    bullet2 = Bullet.Player_Ray(self.rect.x + 32, self.rect.y + 30, (0, -1), self.target_group, self.screen_width, self.screen_height)
                    self.bullet_group.add(bullet2)

                    self.sound = pygame.mixer.Sound('data\sound\weapon\\ray.mp3')
                    self.sound.set_volume(0.05)
                    self.sound.play()
                    
                    self.rays = (bullet1, bullet2)
                    self.can_move = False  # во время стрельбы из "zapper" игрок не может двигаться

                if self.current_frame == 32:  # по окончанию анимации стрельбы убирает луч
                    self.death()
                    self.can_move = True  # по окончанию выстрела, игрок снова может двигаться
                

    class Engine():
        
        class Engine(pygame.sprite.Sprite):  # базовый класс двигателя

            def __init__(self, engine, idle_columns, idle_rows, powering_columns, powering_rows):
                super().__init__()
                self.engine = pygame.image.load(characteristic[engine]['engine_filename'])
                self.rect = self.engine.get_rect()

                # холостой ход
                self.idle_frames = animations.make_frames(characteristic[engine]['idle_filename'], idle_columns, idle_rows)
                self.idle_current_frame = 0
                self.idle_image = self.idle_frames[self.idle_current_frame].copy()

                # рабочее состояние
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
                if self.work:  # если игрок двигается срабатывает анимация работы двигателя
                    if self.powering_current_frame == len(self.powering_frames) - 1:
                        self.powering_current_frame = -1

                    self.powering_current_frame += 1
                    self.powering_image = self.powering_frames[self.powering_current_frame].copy()
                    
                    self.image = self.powering_image
                    self.image.blit(self.engine, (0, 0))

                    self.idle_current_frame = -1
                    self.idle_image = self.powering_frames[self.powering_current_frame]

                else:  # анимация холостого хода
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


class Bullet():
    
    class Bullet(pygame.sprite.Sprite):  # базовый класс пули

        def __init__(self, x, y, direction, cannon_name, target_group, screen_width, screen_height, columns=None, rows=None):
            super().__init__()
            if columns is None: columns = characteristic[cannon_name]['columns']
            if rows is None: rows = characteristic[cannon_name]['rows']

            self.damage = characteristic[cannon_name]['damage']
            self.direction = direction
            self.speed = characteristic[cannon_name]['bullet_speed']
            self.target_group = target_group

            # угол для поворота изображения спрайта
            self.angle = self.get_angle() 
            if self.direction[0] > 0: self.angle = 360 - self.angle 

            self.frames = animations.make_frames(characteristic[cannon_name]['bullet_filename'], columns, rows)
            self.current_frame = 0
            self.image = pygame.transform.rotate(self.frames[self.current_frame], self.angle)
            self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())

            self.rect.x = self.x = x - self.rect.width // 2
            self.rect.y = self.y = y - self.rect.height // 2

            self.screen_height = screen_height
            self.screen_widht = screen_width


        def get_angle(self, vector1=None, vector2=(0, -1)):  # возвращает угол между двумя векторами
            if vector1 is None:
                if self.direction[0] == 0 and self.direction[1] == 0: vector1 = (0.001, 0.001)
                else: vector1 = self.direction

            ma = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
            mb = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)
            sc = vector1[0] * vector2[0] + vector1[1] * vector2[1]
            a = sc / ma / mb
            
            if a > 1: a = 1
            elif a < -1: a = -1
            
            return math.degrees(math.acos(a))
        
        
        def hit(self):  # проверяет столкновения со спрайтами из группы "целей", при попадании наносит урон и исчезает
            for sprite in self.target_group.sprites():
                for group in sprite.groups():
                    if type(group) == Spaceship.Spaceship_Group: 
                        if pygame.sprite.collide_mask(self, sprite):
                            sprite.hurt(self.damage)
                            self.kill()
                            return


        def update(self):
            self.x += self.speed * self.direction[0]
            self.y += self.speed * self.direction[1]

            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = pygame.transform.rotate(self.frames[self.current_frame], self.angle)

            # если пуля вылетает за пределы экрана, она уничтожается
            if self.rect.x + self.rect.width < 0 or\
            self.rect.y + self.rect.height < 0 or\
            self.rect.x > self.screen_widht or\
            self.rect.y > self.screen_height:
                self.kill()
            
            self.hit()


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


    class Enemy_Energy_Bullet(Bullet):

        def __init__(self, x, y, direction, target_group, screen_width, screen_height):
            super().__init__(x, y, direction, 'enemy_energy_bullet', target_group, screen_width, screen_height)


    class Rocket(Bullet):  # базовый класс ракеты

        def __init__(self, x, y, direction, cannon_name, target_group, screen_width, screen_height, columns=None, rows=None):
            super().__init__(x, y, direction, cannon_name, target_group, screen_width, screen_height, columns, rows)
            self.critical_angle = characteristic[cannon_name]['critical_angle']  # максимальный угол захвата
            self.turn_angle = characteristic[cannon_name]['turn_angle']  # максимальный угол поворота за кадр


        def turn(self, angle):  # получает вектор движения из угла
            self.direction = (math.sin(math.radians(angle)), math.cos(math.radians(angle)))


        def update(self):
            targets = []
            for sprite in self.target_group.sprites():
                for group in sprite.groups():
                    if type(group) == Spaceship.Spaceship_Group: 
                        vector = sprite.rect.centerx - self.rect.centerx, sprite.rect.centery - self.rect.centery  # вектор между ракетой и целью
                        angle = self.get_angle(vector2=vector)  # угол между вектором движения ракеты и вектором между ракетой и целью

                        if abs(angle) <= self.critical_angle:  # если цель может быть захваченна
                            # отношение оси х к вектору движения ракеты
                            if self.direction[0] + self.direction[1] == 0 : direction_n = self.direction[0] / 0.0001  
                            else: direction_n = self.direction[0] / (self.direction[0] ** 2 + self.direction[1] ** 2) ** 0.5
                            
                            # отношение оси х к вектору между ракетой и цель.
                            if vector[0] + vector[1] == 0: vector_n = vector[0] / 0.0001
                            else: vector_n = vector[0] / (vector[0] ** 2 + vector[1] ** 2) ** 0.5 

                            # из угла между векторами получает угол поворота
                            if direction_n >= vector_n: turn_angle = angle * -1
                            else: turn_angle = angle

                            if self.rect.centery > sprite.rect.centery:
                                turn_angle *= -1

                            targets.append((turn_angle, ((self.rect.centerx - sprite.rect.centerx) ** 2 + (self.rect.centery - self.rect.centery) ** 2) ** 0.5))

            if len(targets) != 0:
                turn_angle = min(targets, key=lambda x: x[1])[0]  # угол поворота к ближайшей из видимых целей

                if abs(turn_angle) > self.turn_angle:  # если угол поворота больше максимального угла поворота за кадр, угол поворота приравнивается к нему
                    if turn_angle < 0: turn_angle = -self.turn_angle
                    elif turn_angle > 0: turn_angle = self.turn_angle

                # поворот
                self.turn(self.angle + turn_angle + 180)
                self.angle = self.angle + turn_angle

            super().update()


    class Enemy_Rocket(Rocket):

        def __init__(self, x, y, direction, target_group, screen_width, screen_height):
            super().__init__(x, y, direction, 'enemy_rocket', target_group, screen_width, screen_height)


    class Player_Rocket(Rocket):

        def __init__(self, x, y, direction, target_group, screen_width, screen_height):
            super().__init__(x, y, direction, 'rockets_cannon', target_group, screen_width, screen_height, 3, 1)


    class Bomb(Bullet):  # базовый класс бомбы 
        
        def __init__(self, x, y, direction, cannon_name, target_group, screen_width, screen_height, explosion_frames, factor):
            super().__init__(x, y, direction, cannon_name, target_group, screen_width, screen_height)
            self.affected_area = characteristic[cannon_name]['affected_area']  # зона поражения взрывом
            self.death_check = False

            self.explosion_frames = [pygame.transform.scale_by(frame, factor) for frame in explosion_frames]
            self.current_explosion_frame = -1


        def hit(self):  # бомба взрывается если в области поражения оказывается цель
            for sprite in self.target_group.sprites():
                for group in sprite.groups():
                    if type(group) == Spaceship.Spaceship_Group: 
                        if ((sprite.rect.centerx - self.rect.centerx) ** 2 + (sprite.rect.centery - self.rect.centery) ** 2) ** 0.5 <= self.affected_area:
                            sound = pygame.mixer.Sound('data\sound\explosion.mp3')
                            sound.set_volume(0.01)
                            sound.play()
                            
                            self.target = sprite
                            self.death_check = True
                            return


        def update(self):
            if self.death_check:
                if self.current_explosion_frame == -1:
                    x, y = self.rect.centerx, self.rect.centery
                    self.rect = self.explosion_frames[0].get_rect()
                    self.rect.centerx, self.rect.centery = x, y

                self.current_explosion_frame += 1

                if self.current_explosion_frame == len(self.explosion_frames):
                    # если цель всё ещё находится в зоне поражения - ей наносится урон
                    if ((self.target.rect.centerx - self.rect.centerx) ** 2 + (self.target.rect.centery - self.rect.centery) ** 2) ** 0.5 <= self.affected_area:
                        self.target.hurt(self.damage)
                        
                    self.kill()

                else:
                    self.image = self.explosion_frames[self.current_explosion_frame]

            else:
                super().update()


    class Enemy_Bomb(Bomb):

        def __init__(self, x, y, direction, target_group, screen_width, screen_height):
            super().__init__(x, y, direction, 'enemy_bomb', target_group, screen_width, screen_height, animations.make_frames('data\\image\\enemy\\enemy_spaceship\\enemy_bomber\\Nautolan Ship - Bomber.png', 10, 1, cannon=True)[12:], 4)


    class Ray(Bullet):  # базовый класс луча
        
        def __init__(self, x, y, direction, cannon_name, target_group, screen_width, screen_height, columns=None, rows=None):
            super().__init__(x, y, direction, cannon_name, target_group, screen_width, screen_height, columns, rows)
            if direction[1] == -1: self.rect.y -= self.screen_height
            self.draw()


        def draw(self):  # рисует луч на весь экран
            image = pygame.surface.Surface((self.rect.width, self.screen_height), pygame.SRCALPHA, 32)

            for i in range(1, 9999):
                y = i * self.rect.height
                image.blit(self.frames[self.current_frame], (0, y))

                if y + self.rect.height < 0 or\
                y > self.screen_height:
                    break
            
            self.image = image.convert_alpha()
            self.mask = pygame.mask.from_surface(self.image)


        def update(self):
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.draw()
            
            # наносит урон всем кого касается
            for sprite in self.target_group.sprites():
                for group in sprite.groups():
                    if type(group) == Spaceship.Spaceship_Group and type(sprite) != Spaceship.Shield: 
                        if pygame.sprite.collide_mask(self, sprite):
                            sprite.hurt(self.damage)


    class Enemy_Ray(Ray):

        def __init__(self, x, y, direction, target_group, screen_width, screen_height):
            super().__init__(x, y, direction, 'enemy_ray', target_group, screen_width, screen_height)


    class Player_Ray(Ray):

        def __init__(self, x, y, direction, target_group, screen_width, screen_height):
            super().__init__(x, y, direction, 'zapper_cannon', target_group, screen_width, screen_height, 8, 1)


class Other():
    
    class Wall(pygame.sprite.Sprite):  # стена визуально ограничивающая игровое поле

        def __init__(self, start_x, end_x, start_y, end_y, group):
            super().__init__()
            
            surface = pygame.surface.Surface((end_x - start_x + 50, end_y - start_y + 50))
            surface.set_colorkey(pygame.color.Color('black'))
            
            for _ in range(60):
                x, y = random.randrange(0, end_x - 50 - start_x), random.randrange(0 , end_y - 50 - start_y)
                asteroid = pygame.image.load('data\image\other\\background\Asteroid 01 - Base.png')
                surface.blit(asteroid, (x, y))
            
            self.image = surface
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = start_x, start_y
            group.add(self)
            
            
    class Health_Bar(pygame.sprite.Sprite):  # health bar

        def __init__(self, x, y, width, height, image, color, hp, group):
            super().__init__()
            self.original_image = pygame.surface.Surface((width, height))
            self.rect = self.original_image.get_rect()
            self.rect.x, self.rect.y = x, y
            self.color = color

            self.hp = self.max_hp =  hp
            self.pixel = width / hp  # ширина 1 единицы здоровья
            self.wait = 0
            self.frames = 1
            self.healing_flag = False

            self.update_health(hp)
            group.add(self)


        def update_health(self, hp):
            if self.hp != hp:  # если отображаемое здоровье не равно текущему - анимация лечения прекращается
                self.stop_healing()

            self.hp = hp
            self.image = self.original_image.copy()
            width = int(self.hp * self.pixel)
            pygame.draw.rect(self.image, self.color, (0, 0, width, self.rect.height))
                
            if self.healing_flag:  # анимация лечения 
                self.wait += 1
                rect = pygame.surface.Surface((int(self.wait * self.step), self.rect.height))
                rect.set_alpha(50)
                rect.fill(self.color)
                self.image.blit(rect, (int(self.hp * self.pixel), 0))

            # вывод текущее здоровье/максимальное
            text = str(self.hp) + '/' + str(self.max_hp)
            font = pygame.font.Font(None, self.rect.height)
            text = font.render(text, True, pygame.color.Color('white'))
            self.image.blit(text, ((self.rect.width - text.get_width()) // 2, (self.rect.height - text.get_height()) // 2))

            if self.wait > self.frames:  # если прошло больше кадров чем нужно на лечение - количество здоровья обновляется
                self.update_health(self.hp + self.healing_hp)


        def healing(self, hp, frames):  # расчитывает анимацию лечения
            if self.hp + hp > self.max_hp: hp = self.max_hp - self.hp

            self.healing_flag = True
            self.step = (hp * self.pixel) / frames
            self.healing_hp = hp
            self.frames = frames


        def stop_healing(self):  # прекращает лечение
            self.healing_flag = False
            self.wait = 0


    class Stopwatch(pygame.sprite.Sprite):  # таймер

        def __init__(self, x, y, width, height, stopwatch, group):
            super().__init__()

            self.font = pygame.font.Font(None, height)
            self.rect = pygame.rect.Rect(10, y, width - 10, height)
            self.stopwatch = stopwatch
            self.time = 0

            self.update
            group.add(self)


        def update(self):  # каждый кадр увеличивает значение времени и выводит его на экран
            self.time += self.stopwatch.tick()
            text = f'{self.time // 1000 // 60}:{self.time // 1000 % 60}:{str(self.time % 1000)[:2]}'
            self.image = self.font.render(text, self.rect.height, pygame.color.Color('white'))

