import pygame
import get_settings
import classes


FPS = 60

def settings(lvl_name):
    player = get_settings.create_player_ship()
    
    if player[2] == 'auto_cannon': player.insert(2, classes.Game.Auto_Cannon)
    elif player[2] == 'big_space_cannon': player.insert(2, classes.Game.Big_Space_Cannon)

    if player[4] == 'base_engine': player.insert(4, classes.Game.Base_Engine)

    enemy_placement = get_settings.enemy_placement(lvl_name)

    player.append(enemy_placement)
    return player

def create_lvl(screen, lvl_name):
    width = 800
    height = screen.get_height()
    x = (screen.get_width() - 800) // 2
    y = 0

    s = settings(lvl_name)

    hud_group = pygame.sprite.Group()
    spaceships_group = classes.Game.Spaceship_Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    player_bullet_group = pygame.sprite.Group()
    enemy_bullet_group = pygame.sprite.Group()

    game_group = classes.Game.Game_Group()
    game_group.add(player_bullet_group, player_group, enemy_bullet_group, enemy_group, hud_group)
    
    player = classes.Game.Player_Spaceship(400 + x, height * 0.75, (x, y + height // 2, x + 800, height), screen.get_width(), height, spaceships_group, player_bullet_group, enemy_group, player_group, *s[:-1], x + width + 20, 20, (screen.get_width() - width) // 2 - 44, 30, hud_group)

    wall1 = classes.Game.Wall(x - 4, y, y + height, hud_group)
    wall2 = classes.Game.Wall(x + 800, y, y + height, hud_group)

    set_up_enemies(s[-1][0], spaceships_group, enemy_bullet_group, player_group, enemy_group, height, screen.get_width(), x, y)

    return player, game_group, enemy_group, (spaceships_group, enemy_bullet_group, player_group, enemy_group, height, screen.get_width(), x, y), s[-1][1:]

def set_up_enemies(placement, spaceships_group, enemy_bullet_group, player_group, enemy_group, screen_height, screen_width, x, y):
    pos_height = (screen_height / 2) // len(placement)

    for pos_y in range(len(placement)):
        width = 800 // len(placement[pos_y])
        for pos_x in range(len(placement[pos_y])):
            if placement[pos_y][pos_x] == '-':
                continue
            
            elif placement[pos_y][pos_x] == 'fi':
                enemy = classes.Game.Enemy_Fighter(int(width * (pos_x + 0.5)) + x, int((pos_y + 0.5) * pos_height), (x, 0, x + 800, y + screen_height // 2), spaceships_group, enemy_bullet_group, player_group, enemy_group, screen_width, screen_height)

            elif placement[pos_y][pos_x] == 'fr':
                enemy = classes.Game.Enemy_Frigate(int(width * (pos_x + 0.5)) + x, int((pos_y + 0.5) * pos_height), (x, 0, x + 800, y + screen_height // 2), spaceships_group, enemy_bullet_group, player_group, enemy_group, screen_width, screen_height)

            elif placement[pos_y][pos_x] == 'to':
                enemy = classes.Game.Enemy_Torpedo(int(width * (pos_x + 0.5)) + x, int((pos_y + 0.5) * pos_height), (x, 0, x + 800, y + screen_height // 2), spaceships_group, enemy_bullet_group, player_group, enemy_group, screen_width, screen_height)

            elif placement[pos_y][pos_x] == 'sc':
                enemy = classes.Game.Enemy_Scout(int(width * (pos_x + 0.5)) + x, int((pos_y + 0.5) * pos_height), (x, 0, x + 800, y + screen_height // 2), spaceships_group, enemy_bullet_group, player_group, enemy_group, screen_width, screen_height)

            elif placement[pos_y][pos_x] == 'bo':
                enemy = classes.Game.Enemy_Bomber(int(width * (pos_x + 0.5)) + x, int((pos_y + 0.5) * pos_height), (x, 0, x + 800, y + screen_height // 2), spaceships_group, enemy_bullet_group, player_group, enemy_group, screen_width, screen_height)

            elif placement[pos_y][pos_x] == 'bc':
                enemy = classes.Game.Enemy_Battlecruiser(int(width * (pos_x + 0.5)) + x, int((pos_y + 0.5) * pos_height), (x, 0, x + 800, y + screen_height // 2), spaceships_group, enemy_bullet_group, player_group, enemy_group, screen_width, screen_height)

            elif placement[pos_y][pos_x] == 'dn':
                enemy = classes.Game.Enemy_Dreadnought(int(width * (pos_x + 0.5)) + x, int((pos_y + 0.5) * pos_height), (x, 0, x + 800, y + screen_height // 2), spaceships_group, enemy_bullet_group, player_group, enemy_group, screen_width, screen_height)

def game(screen):
    player, game_group, enemy_group, sue_settings, placements = create_lvl(screen, '1.txt')

    keys = {'up': False, 'down': False, 'left': False, 'right': False, 'shoot': False}
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    keys['up'] = True
                
                elif event.key == pygame.K_s:
                    keys['down'] = True

                elif event.key == pygame.K_a:
                    keys['left'] = True
                
                elif event.key == pygame.K_d:
                    keys['right'] = True

                elif event.key == pygame.K_SPACE:
                    keys['shoot'] = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    keys['up'] = False
                
                elif event.key == pygame.K_s:
                    keys['down'] = False

                elif event.key == pygame.K_a:
                    keys['left'] = False
                
                elif event.key == pygame.K_d:
                    keys['right'] = False

                elif event.key == pygame.K_SPACE:
                    keys['shoot'] = False

            elif event.type == pygame.QUIT:
                running = False

        if keys['up']: player.move(0, -1)
        if keys['down']: player.move(0, 1)
        if keys['left']: player.move(-1, 0)
        if keys['right']: player.move(1, 0)
        if keys['shoot']: player.shoot()

        screen.fill(pygame.Color('black'))
        game_group.update()
        game_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

        if len(enemy_group.sprites()) == 0:
            if len(placements) == 0:
                running = False

            else:
                set_up_enemies(placements.pop(0), *sue_settings)

        if player.death_check:
            running = False

def create_buttons_group(data, text=False, text_color='black', background_color=None, border=0, border_color='white'):
    group = classes.Menu.Button_Group()
    for d in data:
        button = classes.Menu.Button(*d, text=text, text_color=text_color, background_color=background_color, border=border, border_color=border_color)
        group.add(button)

    return group

def create_menu_buttons(x, y, width, height, signal):
    step = height // 8
    txt = ['Играть', 'Корабль', 'Настройки', 'Выйти']
    data = [(x + width // 2, y + height // 18 + i * step, signal + i + 1, txt[i], None, (width // 2, height // 9)) for i in range(4)]
    main_buttons = create_buttons_group(data, text=True, text_color='white', background_color='black', border=4)
    signal += 4

    image = pygame.image.load('data\\image\\other\\icons8-стрелка-100.png')
    image.set_colorkey(pygame.color.Color('black'))
    images = [pygame.transform.rotate(image, 180 * i) for i in range(1, 5)]
    data = [(x // 2, height // 4,), (x * 1.5 + width, height // 4), (x // 2, height // 3 * 2), (x * 1.5 + width, height // 3 * 2)]
    data = [(*data[i], signal + i + 1, images[i], None, (100, 100)) for i in range(4)]
    spaceship_characteristic_buttons = create_buttons_group(data)
    spaceship_characteristic_buttons.add(classes.Menu.Button(x + width // 2, height // 10 * 9, signal + 5, 'Назад', None, ((width + x * 2) // 12, height // 14), text=True, text_color='white', background_color='black', border=4))
    signal += 5
    
    characteristic = get_settings.characteristic()
    images = ([pygame.transform.scale_by(pygame.image.load(filename), height // 4 / pygame.image.load(filename).get_rect().height) for filename in ('data\\image\\player\\cannon\\auto_cannon\Main Ship - Auto Cannon Base.png', 'data\\image\\player\\cannon\\big_space_gun\\Main Ship - Big Space Gun Base.png', 'data\\image\\player\\cannon\\rockets\\Main Ship - Rockets Base.png', 'data\\image\\player\\cannon\\zapper\\Main Ship - Zapper Base.png')], True)
    texts1 = (('Обычная автоматическая пушка', 'Мощное плазменное оружие', 'Установка самонаводящихся ракет', 'Звезда смерти на минималках'), False)
    texts2 = ((f'Урон: {characteristic['auto_cannon']['damage']}, Перезарядка: {characteristic['auto_cannon']['reload']}, Скорость снаряда: {characteristic['auto_cannon']['bullet_speed']}',
               f'Урон: {characteristic['big_space_cannon']['damage']}, Перезарядка: {characteristic['big_space_cannon']['reload']}, Скорость снаряда: {characteristic['big_space_cannon']['bullet_speed']}',
               f'Урон: {characteristic['rockets_cannon']['damage']}, Перезарядка: {characteristic['rockets_cannon']['reload']}, Скорость ракеты: {characteristic['rockets_cannon']['bullet_speed']}, Предельный угол захвата ракеты: {characteristic['rockets_cannon']['critical_angle']}',
               f'Максимальный урон за выстрел: {characteristic['zapper_cannon']['damage'] * 20}, Перезарядка: {characteristic['zapper_cannon']['reload']}'), False)
    names = ('auto_cannon', 'big_space_cannon', 'rockets_cannon', 'zapper_cannon')
    cannon_info_group = classes.Menu.Data(x + width // 2, height // 4, (images, texts1, texts2), height // 30, 'white', names)
    spaceship_characteristic_buttons.add(cannon_info_group)
    spaceship_characteristic_buttons.dict['cannon_info'] = cannon_info_group

    images = ([pygame.transform.scale_by(pygame.image.load(filename), height // 4 / pygame.image.load(filename).get_rect().height) for filename in ('data\\image\\player\\shield\\Main Ship - Invencibility Shield Base.png', 'data\\image\\player\\shield\\Main Ship - Front and Side Shield Base.png', 'data\\image\\player\\shield\\Main Ship - Round Shield Base.png')], True)
    texts1 = (('Маленький щит который можно быстро восстановить', 'Средний щит, на восстановление потребуется время', 'Большой щит требующий много времени на восстановление'), False)
    texts2 = ((f'Прочность: {characteristic['shield_1']['shield_hp']}, Перезарядка: {characteristic['shield_1']['shield_reload'] / 60} секунд',
               f'Прочность: {characteristic['shield_2']['shield_hp']}, Перезарядка: {characteristic['shield_2']['shield_reload'] / 60} секунд',
               f'Прочность: {characteristic['shield_3']['shield_hp']}, Перезарядка: {characteristic['shield_3']['shield_reload'] / 60} секунд'), False)
    names = ('shield_1', 'shield_2', 'shield_3')
    shield_info_group = classes.Menu.Data(x + width // 2, height // 3 * 2, (images, texts1, texts2), height // 30, 'white', names)
    spaceship_characteristic_buttons.add(shield_info_group)
    spaceship_characteristic_buttons.dict['shield_info'] = shield_info_group

    txt = ['wasd + space', 'mouse', 'Назад']
    data = [[x + width * i, height // 2, signal + i + 1, txt[i], None, ((width + x * 2) // 4, height // 4)] for i in range(3)]
    data[2][0], data[2][1], data[2][5] = x + width // 2, height // 10 * 9, ((width + x * 2) // 12, height // 14)
    setting_buttons = create_buttons_group(data, text=True, text_color='White', border=4)
    signal += 3

    return main_buttons, spaceship_characteristic_buttons, setting_buttons

def main_menu(screen):
    width = 800
    height = screen.get_height()
    x = (screen.get_width() - 800) // 2
    signal = pygame.USEREVENT
    main_menu_buttons, spaceships_characteristic_buttons, setting_buttons = create_menu_buttons(x, height // 4, width, height, signal)
    main_buttons = main_menu_buttons
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                main_buttons.update(event.pos, False)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                main_buttons.update(event.pos, True)

            elif event.type == pygame.USEREVENT + 1:
                game(screen)
                main_buttons.update((0, 0), False)

            elif event.type == pygame.USEREVENT + 2:
                main_buttons = spaceships_characteristic_buttons

            elif event.type == pygame.USEREVENT + 3:
                main_buttons = setting_buttons
            
            elif event.type == pygame.USEREVENT + 4 or event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.USEREVENT + 5:
                spaceships_characteristic_buttons.dict['cannon_info'].previous()

                with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                    data = file.readlines()
                    data[2] = spaceships_characteristic_buttons.dict['cannon_info'].get_current_objectname() + '\n'
                
                with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                    file.writelines(data)
 
            elif event.type == pygame.USEREVENT + 6:
                spaceships_characteristic_buttons.dict['cannon_info'].next()
                with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                    data = file.readlines()
                    data[2] = spaceships_characteristic_buttons.dict['cannon_info'].get_current_objectname() + '\n'
                
                with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                    file.writelines(data)

            elif event.type == pygame.USEREVENT + 7:
                spaceships_characteristic_buttons.dict['shield_info'].previous()
                with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                    data = file.readlines()
                    data[2] = spaceships_characteristic_buttons.dict['shield_info'].get_current_objectname() + '\n'
                
                with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                    file.writelines(data)

            elif event.type == pygame.USEREVENT + 8:
                spaceships_characteristic_buttons.dict['shield_info'].next()
                with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                    data = file.readlines()
                    data[2] = spaceships_characteristic_buttons.dict['shield_info'].get_current_objectname() + '\n'
                    
                with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                    file.writelines(data)

            elif event.type == pygame.USEREVENT + 9 or event.type == pygame.USEREVENT + 12:
                main_buttons = main_menu_buttons

            elif event.type == pygame.USEREVENT + 10:
                with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                    data = file.readlines()
                    data[4] = '0'
                    
                with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                    file.writelines(data)

            elif event.type == pygame.USEREVENT + 11:
                with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                    data = file.readlines()
                    data[4] = '1'
                    
                with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                    file.writelines(data)

        screen.fill(pygame.color.Color('black'))
        main_buttons.draw(screen)
        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    main_menu(screen)
    pygame.quit()

if __name__ == '__main__':
    main()
    