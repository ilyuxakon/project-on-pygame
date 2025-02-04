import pygame
import get_settings
import classes
import sqlite3


FPS = 60


def settings(lvl_name):
    player = get_settings.create_player_ship()
    
    if player[2] == 'auto_cannon': player.insert(2, classes.Game.Auto_Cannon)
    elif player[2] == 'big_space_cannon': player.insert(2, classes.Game.Big_Space_Cannon)
    elif player[2] == 'rockets_cannon': player.insert(2, classes.Game.Rockets_Cannon)
    elif player[2] == 'zapper_cannon': player.insert(2, classes.Game.Zapper_Cannon)

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
    
    player = classes.Game.Player_Spaceship(400 + x, height * 0.75, (x, y + height // 2, x + 800, height), screen.get_width(), height, spaceships_group, player_bullet_group, enemy_group, player_group, *s[:-3], x + width + 20, 20, (screen.get_width() - width) // 2 - 44, height // 20, hud_group)

    stopwatch = classes.Game.Stopwatch(0, 0, x, height // 20, pygame.time.Clock(), hud_group)
    wall1 = classes.Game.Wall(x - 4, y, y + height, hud_group)
    wall2 = classes.Game.Wall(x + 800, y, y + height, hud_group)

    set_up_enemies(s[-1][0], spaceships_group, enemy_bullet_group, player_group, enemy_group, height, screen.get_width(), x, y)

    return player, stopwatch, game_group, enemy_group, (spaceships_group, enemy_bullet_group, player_group, enemy_group, height, screen.get_width(), x, y), s[-1][1:], s[6]


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


def game(screen, lvl):
    player, stopwatch, game_group, enemy_group, sue_settings, placements, setting = create_lvl(screen, lvl + '.txt')

    pygame.mouse.set_visible(False)
    keys = {'up': False, 'down': False, 'left': False, 'right': False, 'shoot': False}
    clock = pygame.time.Clock()
    
    mouse_move = False
    width, height = screen.get_rect().width // 2, screen.get_rect().height // 2

    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if setting == '0':
                    if event.key == pygame.K_w:
                        keys['up'] = True
                    
                    elif event.key == pygame.K_s:
                        keys['down'] = True

                    elif event.key == pygame.K_d:
                        keys['right'] = True
                    
                    elif event.key == pygame.K_a:
                        keys['left'] = True

                    elif event.key == pygame.K_SPACE:
                        keys['shoot'] = True

                if event.key == pygame.K_ESCAPE:
                    image1 = pygame.surface.Surface((screen.get_rect().width, screen.get_rect().height), pygame.SRCALPHA)
                    image1.blit(screen, (0, 0))
                    image1.set_alpha(128)
                    image2 = pygame.surface.Surface((800 // 3 * 2, screen.get_rect().height // 2), pygame.SRCALPHA)
                    image2.fill(pygame.color.Color('black'))
                    image2.set_alpha(128)                    
                    image3 = pygame.surface.Surface((800 // 3 * 2, screen.get_rect().height // 2))
                    image3.set_colorkey(pygame.color.Color('black'))
                    pygame.draw.lines(image3, pygame.color.Color('white'), True, ((0, 0), (800 // 3 * 2 - 2, 0), (800 // 3 * 2 - 2, screen.get_rect().height // 2 - 2), (0, screen.get_rect().height // 2 - 2)), 2)
                    background_image = pygame.surface.Surface((screen.get_rect().width, screen.get_rect().height))
                    background_image.blit(image1, (0, 0))
                    background_image.blit(image2, (screen.get_rect().width // 2 - 800 // 3, screen.get_rect().height // 4))
                    background_image.blit(image3, (screen.get_rect().width // 2 - 800 // 3, screen.get_rect().height // 4))
                    background_sprite = pygame.sprite.Sprite()
                    background_sprite.image = background_image
                    background_sprite.rect = background_image.get_rect()
                    background = pygame.sprite.Group()
                    background.add(background_sprite)

                    if esc_menu(screen, background, stopwatch.time, score):
                        main_menu(screen)
                        return
                    
                    with open('settings\\current_player_settings.txt', 'r', encoding='utf-8') as file:
                        setting = file.readlines()[4].strip()

                    keys = {'up': False, 'down': False, 'left': False, 'right': False, 'shoot': False}
                    stopwatch.stopwatch.tick()

            elif event.type == pygame.KEYUP:
                if setting == '0':
                    if event.key == pygame.K_w:
                        keys['up'] = False
                    
                    elif event.key == pygame.K_s:
                        keys['down'] = False

                    elif event.key == pygame.K_d:
                        keys['right'] = False
                    
                    elif event.key == pygame.K_a:
                        keys['left'] = False

                    elif event.key == pygame.K_SPACE:
                        keys['shoot'] = False

            elif event.type == pygame.MOUSEMOTION:
                if setting == '1':
                    x, y = event.rel[0], event.rel[1]
                    
                    if x != 0 and y != 0:
                        keys['down'] = y / (abs(x) + abs(y))
                        keys['right'] = x / (abs(x) + abs(y))
                        mouse_move = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if setting == '1':
                    keys['shoot'] = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if setting == '1':
                    keys['shoot'] = False

            elif event.type == pygame.USEREVENT:
                score += 100

            elif event.type == pygame.QUIT:
                running = False

        if setting == '1':
            if mouse_move == False:
                keys['down'] = 0
                keys['right'] = 0

            mouse_move = False
            pygame.mouse.set_pos(width, height)
            pygame.mouse.get_rel()

            player.move(keys['right'], keys['down'])

        else:
            if keys['up']: player.move(0, -1)
            if keys['down']: player.move(0, 1)
            if keys['left']: player.move(-1, 0)
            if keys['right']: player.move(1, 0)

        if keys['shoot']: player.shoot()

        screen.fill(pygame.color.Color('black'))
        game_group.update()
        game_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

        if len(enemy_group.sprites()) == 0:
            if len(placements) == 0:
                score += 100
                running = False
                win = True

            else:
                set_up_enemies(placements.pop(0), *sue_settings)

        if player.death_check:
            running = False
            win = False

    con = sqlite3.connect('levels\\record.sqlite')
    cur = con.cursor()
    cur.execute('INSERT INTO record VALUES (?, ?, ?)', (int(lvl), score, stopwatch.time))
    con.commit()
    
    with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
        data = file.readlines()
        if int(data[5].strip()) < int(lvl): data[5] = lvl
        
    with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
        file.writelines(data)
    
    image1 = pygame.surface.Surface((screen.get_rect().width, screen.get_rect().height), pygame.SRCALPHA)
    image1.blit(screen, (0, 0))
    image1.set_alpha(128)
    image2 = pygame.surface.Surface((screen.get_width(), screen.get_rect().height // 3 * 2), pygame.SRCALPHA)
    image2.fill(pygame.color.Color('black'))
    image2.set_alpha(128)                    
    background_image = pygame.surface.Surface((screen.get_rect().width, screen.get_rect().height))
    background_image.blit(image1, (0, 0))
    background_image.blit(image2, (0, screen.get_rect().height // 6))
    background_sprite = pygame.sprite.Sprite()
    background_sprite.image = background_image
    background_sprite.rect = background_image.get_rect()
    background = pygame.sprite.Group()
    background.add(background_sprite)

    end_menu(screen, background, stopwatch.time, score, win, lvl)
    main_menu(screen)
    
    
def create_buttons_group(data, text=False, text_color='black', background_color=None, background=None, border=0, border_color='white'):
    group = classes.Menu.Button_Group()
    for d in data:
        button = classes.Menu.Button(*d, text=text, text_color=text_color, background_color=background_color, background=background, border=border, border_color=border_color)
        group.add(button)

    return group


def create_main_menu(x, y, width, height, signal):
    with open('settings\\current_player_settings.txt', 'r', encoding='utf-8') as file:
        file = file.readlines()
        s, lvl = int(file[4]), int(file[5])

    txt = ['Играть', 'Корабль', 'Настройки', 'Выйти']
    data = [(x + width // 2, y + height // 18 + i * height // 8, signal + i + 1, txt[i], (width // 2, height // 9)) for i in range(4)]
    main_buttons = create_buttons_group(data, text=True, text_color='white', background_color='black', border=4)
    signal += 4

    image = pygame.image.load('data\\image\\other\\icons8-стрелка-100.png')
    image.set_colorkey(pygame.color.Color('black'))
    images = [pygame.transform.rotate(image, 180 * i) for i in range(1, 5)]
    data = [(x // 2, height // 4,), (x * 1.5 + width, height // 4), (x // 2, height // 3 * 2), (x * 1.5 + width, height // 3 * 2)]
    data = [(*data[i], signal + i + 1, images[i], (100, 100)) for i in range(4)]
    spaceship_characteristic_buttons = create_buttons_group(data)
    spaceship_characteristic_buttons.add(classes.Menu.Button(x + width // 2, height // 10 * 9, signal + 5, 'Назад', ((width + x * 2) // 12, height // 14), text=True, text_color='white', background_color='black', border=4))
    signal += 5
    
    characteristic = get_settings.characteristic()
    images = ([pygame.transform.scale_by(pygame.image.load(filename), height // 4 / pygame.image.load(filename).get_rect().height) for filename in ('data\\image\\player\\cannon\\auto_cannon\Main Ship - Auto Cannon Base.png', 'data\\image\\player\\cannon\\big_space_gun\\Main Ship - Big Space Gun Base.png', 'data\\image\\player\\cannon\\rockets\\Main Ship - Rockets Base.png', 'data\\image\\player\\cannon\\zapper\\Main Ship - Zapper Base.png')], 1)
    texts1 = (('Обычная автоматическая пушка', 'Мощное плазменное оружие', 'Установка самонаводящихся ракет', 'Звезда смерти на минималках'), 2)
    texts2 = ((f'Урон: {characteristic['auto_cannon']['damage']}, Перезарядка: {characteristic['auto_cannon']['reload']}, Скорость снаряда: {characteristic['auto_cannon']['bullet_speed']}',
               f'Урон: {characteristic['big_space_cannon']['damage']}, Перезарядка: {characteristic['big_space_cannon']['reload']}, Скорость снаряда: {characteristic['big_space_cannon']['bullet_speed']}',
               f'Урон: {characteristic['rockets_cannon']['damage']}, Перезарядка: {characteristic['rockets_cannon']['reload']}, Скорость ракеты: {characteristic['rockets_cannon']['bullet_speed']}, Предельный угол захвата ракеты: {characteristic['rockets_cannon']['critical_angle']}',
               f'Максимальный урон за выстрел: {characteristic['zapper_cannon']['damage'] * 20}, Перезарядка: {characteristic['zapper_cannon']['reload']}'), 2)
    names = ('auto_cannon', 'big_space_cannon', 'rockets_cannon', 'zapper_cannon')
    cannon_info_group = classes.Menu.Data(x + width // 2, height // 4, (images, texts1, texts2), height // 30, 'white', names, lvl + 1)
    
    with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
        cannon_name = file.readlines()[2].strip()
        while True:
            cannon_info_group.next()
            if cannon_info_group.get_current_objectname() == cannon_name:
                break
            
    spaceship_characteristic_buttons.add(cannon_info_group)
    spaceship_characteristic_buttons.dict['cannon_info'] = cannon_info_group

    images = ([pygame.transform.scale_by(pygame.image.load(filename), height // 4 / pygame.image.load(filename).get_rect().height) for filename in ('data\\image\\player\\shield\\Main Ship - Invencibility Shield Base.png', 'data\\image\\player\\shield\\Main Ship - Front and Side Shield Base.png', 'data\\image\\player\\shield\\Main Ship - Round Shield Base.png')], 1)
    texts1 = (('Маленький щит который можно быстро восстановить', 'Средний щит, на восстановление потребуется время', 'Большой щит требующий много времени на восстановление'), 2)
    texts2 = ((f'Прочность: {characteristic['shield_1']['shield_hp']}, Перезарядка: {characteristic['shield_1']['shield_reload'] / 60} секунд',
               f'Прочность: {characteristic['shield_2']['shield_hp']}, Перезарядка: {characteristic['shield_2']['shield_reload'] / 60} секунд',
               f'Прочность: {characteristic['shield_3']['shield_hp']}, Перезарядка: {characteristic['shield_3']['shield_reload'] / 60} секунд'), 2)
    names = ('shield_1', 'shield_2', 'shield_3')
    shield_info_group = classes.Menu.Data(x + width // 2, height // 3 * 2, (images, texts1, texts2), height // 30, 'white', names, 3)

    with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
        shield_name = file.readlines()[1].strip()
        while True:
            shield_info_group.next()
            if shield_info_group.get_current_objectname() == shield_name:
                break
            
            
    spaceship_characteristic_buttons.add(shield_info_group)
    spaceship_characteristic_buttons.dict['shield_info'] = shield_info_group

    txt = ['wasd + space', 'mouse']
    data = [[x + width * i, height // 2, signal + i + 1, txt[i], ((width + x * 2) // 4, height // 4)] for i in range(2)]
    setting1 = classes.Menu.Switch_Button_Group(create_buttons_group(data, text=True, text_color='White', border=4), s)
    setting2 = create_buttons_group(((x + width // 2, height // 10 * 9, signal + 3, 'Назад', ((width + x * 2) // 12, height // 14,)),), text=True, text_color='white', border=4)
    setting_buttons = classes.Menu.Group_Group()
    setting_buttons.add(setting1)
    setting_buttons.add(setting2)
    signal += 3
    
    txt = ['Назад', 'Играть']
    data = [(x + width // 4, height // 10 * 9), (x + width // 4 * 3, height // 10 * 9)]
    data = [(*data[i], signal + i + 1, txt[i], ((width + x * 2) // 6, height // 8,)) for i in range(2)]
    lvl_buttons1 = create_buttons_group(data, text=True, text_color='white', border=4)
    signal += 2
    image = pygame.image.load('data\\image\\other\\icons8-стрелка-100.png')
    image.set_colorkey(pygame.color.Color('black'))
    images = [pygame.transform.rotate(image, 180 * i) for i in range(1, 5)]
    data = [(x // 2, height // 2), (x * 1.5 + width, height // 2)]
    data = [(*data[i], signal + i + 1, images[i], (100, 100)) for i in range(2)]
    lvl_buttons2 = create_buttons_group(data)
    con = sqlite3.connect('levels\\record.sqlite')
    cur = con.cursor()
    lvls = [cur.execute("""SELECT score, time FROM record
                          WHERE lvl == ?""", (i,)).fetchall() for i in range(1, 5)]
    lvls = [sorted(lvl, key=lambda x: (int(x[0]), int(x[1] * -1)), reverse=True)[:5] for lvl in lvls]
    font = pygame.font.Font(None, height // 20)
    for i in range(len(lvls)):
        new_lvls = [' #  ', ' #1 ', ' #2 ', ' #3 ', ' #4 ', ' #5 ', ' Счет']
        if lvls[i] == []:
            new_lvls.extend(['-                   ' for _ in range(5)])
            new_lvls.append(' Время')
            new_lvls.extend(['-                   ' for _ in range(5)])

        else:
            n = len(lvls[i])
            new_lvls.extend([str(lvls[i][u][0]) for u in range(n)])

            if n < 5:
                new_lvls.extend([' -                   ' for _ in range(5 - n)])

            new_lvls.append(' Время')
            new_lvls.extend([f'{lvls[i][u][1] // 1000 // 60}:{lvls[i][u][1] // 1000 % 60}:{str(lvls[i][u][1] % 1000)[:2]}' for u in range(n)])

            if n < 5:
                new_lvls.extend([' -                   ' for _ in range(5 - n)])

        lvls[i] = [[(font.render(text, True, pygame.color.Color('white')),) for text in new_lvls],]
        lvls[i].extend((3, 1))
    lvls.append(3)

    text = [('Уровень: 1', 'Уровень: 2', 'Уровень: 3', 'Уровень: 4'), 2]

    lvls_data = classes.Menu.Data(x + width // 2, height // 5 * 2, (text, (height // 6, 4), lvls), height // 10, 'white', ('1', '2', '3', '4'), lvl + 1)
    lvl_buttons = classes.Menu.Group_Group()
    
    lvl_buttons.add(lvl_buttons1)
    lvl_buttons.add(lvl_buttons2)
    lvl_buttons.add(lvls_data)
    lvl_buttons.dict['lvl'] = lvls_data

    return main_buttons, spaceship_characteristic_buttons, setting_buttons, lvl_buttons


def main_menu(screen):
    width = 800
    height = screen.get_height()
    x = (screen.get_width() - 800) // 2
    signal = pygame.USEREVENT
    main_menu_buttons, spaceships_characteristic_buttons, setting_buttons, lvl_buttons = create_main_menu(x, height // 4, width, height, signal)
    main_buttons = main_menu_buttons
    
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                main_buttons.update(event.pos, False)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                main_buttons.update(event.pos, True)

            elif event.type == pygame.USEREVENT + 1:
                main_buttons = lvl_buttons

            elif event.type == pygame.USEREVENT + 2:
                main_buttons = spaceships_characteristic_buttons
                main_buttons.update((0, 0), False)

            elif event.type == pygame.USEREVENT + 3:
                main_buttons = setting_buttons
                main_buttons.update((0, 0), False)
            
            elif event.type == pygame.USEREVENT + 4 or event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.USEREVENT + 5:
                if spaceships_characteristic_buttons.dict['cannon_info'].previous():
                    with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                        data = file.readlines()
                        data[2] = spaceships_characteristic_buttons.dict['cannon_info'].get_current_objectname() + '\n'
                    
                    with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                        file.writelines(data)
 
            elif event.type == pygame.USEREVENT + 6:
                if spaceships_characteristic_buttons.dict['cannon_info'].next():
                    with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                        data = file.readlines()
                        data[2] = spaceships_characteristic_buttons.dict['cannon_info'].get_current_objectname() + '\n'
                    
                    with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                        file.writelines(data)

            elif event.type == pygame.USEREVENT + 7:
                if spaceships_characteristic_buttons.dict['shield_info'].previous():
                    with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                        data = file.readlines()
                        data[1] = spaceships_characteristic_buttons.dict['shield_info'].get_current_objectname() + '\n'
                    
                    with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                        file.writelines(data)

            elif event.type == pygame.USEREVENT + 8:
                if spaceships_characteristic_buttons.dict['shield_info'].next():
                    with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                        data = file.readlines()
                        data[1] = spaceships_characteristic_buttons.dict['shield_info'].get_current_objectname() + '\n'
                        
                    with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                        file.writelines(data)

            elif event.type == pygame.USEREVENT + 9 or event.type == pygame.USEREVENT + 12 or event.type == pygame.USEREVENT + 13:
                main_buttons = main_menu_buttons
                main_buttons.update((0, 0), False)

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

            elif event.type == pygame.USEREVENT + 14:
                game(screen, lvl_buttons.dict['lvl'].get_current_objectname())
                running = False
            
            elif event.type == pygame.USEREVENT + 15:
                lvl_buttons.dict['lvl'].previous()

            elif event.type == pygame.USEREVENT + 16:
                lvl_buttons.dict['lvl'].next()

        screen.fill(pygame.color.Color('black'))
        main_buttons.draw(screen)
        pygame.display.flip()


def create_esc_menu(x, y, width, height, signal, time, score):
    with open('settings\\current_player_settings.txt', 'r', encoding='utf-8') as file:
        s = int(file.readlines()[4])

    text1 = (f'Текущий счёт: {score}',)
    text2 = (f'Текущее время: {time // 1000 // 60}:{time // 1000 % 60}:{str(time % 1000)[:2]}',)
    text_group = classes.Menu.Data(x + width // 2, y + height // 16, ((text1, 2), (text2, 2)), height // 30, 'white', (None), -1)
    txt = ['Продолжить', 'Настройки', 'Выйти']
    data = [(x + width // 2, y + height // 8 * (i + 1.5), signal + i + 1, txt[i], (width // 3, height // 9)) for i in range(3)]
    esc_buttons = create_buttons_group(data, text=True, text_color='white', background_color='black', border=4)
    signal += 3

    main_buttons = classes.Menu.Group_Group()
    main_buttons.add(text_group)
    main_buttons.add(esc_buttons)

    txt = ['wasd + space', 'mouse']
    data = [[x + width // 2, y + height // 18 + (i + 0.5) * height // 8, signal + i + 1, txt[i], (width // 3, height // 9)] for i in range(2)]
    setting1 = classes.Menu.Switch_Button_Group(create_buttons_group(data, text=True, text_color='White', border=4), s)
    setting2 = create_buttons_group(((x + width // 2, y + height // 18 + 2.5 * height // 8, signal + 3, 'Назад', (width // 3, height // 9)),), text=True, text_color='white', border=4)
    setting_buttons = classes.Menu.Group_Group()
    setting_buttons.add(setting1)
    setting_buttons.add(setting2)

    return main_buttons, setting_buttons


def esc_menu(screen, background, time, score):
    pygame.mouse.set_visible(True)

    width = 800
    height = screen.get_height()
    x = (screen.get_width() - 800) // 2
    signal = pygame.USEREVENT
    esc_buttons, setting_buttons = create_esc_menu(x, height // 4, width, height, signal, time, score)
    main_buttons = esc_buttons

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                main_buttons.update(event.pos, False)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                main_buttons.update(event.pos, True)

            if event.type == pygame.USEREVENT + 1:
                pygame.mouse.set_visible(False)
                return False

            elif event.type == pygame.USEREVENT + 2:
                main_buttons = setting_buttons
                main_buttons.update((0, 0), False)
            
            elif event.type == pygame.USEREVENT + 3:
                return True

            elif event.type == pygame.USEREVENT + 4:
                with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                    data = file.readlines()
                    data[4] = '0\n'
                    
                with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                    file.writelines(data)

            elif event.type == pygame.USEREVENT + 5:
                with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as file:
                    data = file.readlines()
                    data[4] = '1\n'
                    
                with open('settings\current_player_settings.txt', 'w', encoding='utf-8') as file:
                    file.writelines(data)

            elif event.type == pygame.USEREVENT + 6:
                main_buttons = esc_buttons
                main_buttons.update((0, 0), False)


        screen.fill(pygame.color.Color('black'))
        background.draw(screen)
        main_buttons.draw(screen)
        pygame.display.flip()


def create_end_menu(x, y, width, height, signal, time, score, win, lvl):
    font = pygame.font.Font(None, height // 8)
    if win: texthd, color = 'Вы победили', 'green'
    else: texthd, color = 'Поражение', 'red'
    
    result = classes.Menu.Text(x + width // 2, y + height // 5, height // 10, (texthd,), color)
    
    con = sqlite3.connect('levels\\record.sqlite')
    cur = con.cursor()
    lvl = cur.execute("""SELECT score, time FROM record
                          WHERE lvl == ?""", (int(lvl),)).fetchall()
    lvl.sort(key=lambda x: (x[0], -x[1]), reverse=True)
    i = lvl.index((score, time))
    font = pygame.font.Font(None, height // 15)
    
    if i > 2:
        new_lvl = [' #  ', f' #{i - 1} ', f' #{i} ', f' #{i + 1} ', f' #{i + 2} ', f' #{i + 3} ', ' Счёт']
    
    else: 
        new_lvl = [' #  ', ' #1 ', ' #2 ', ' #3 ', ' #4 ', ' #5 ', ' Счёт']
    
    new_lvl = [(font.render(t, True, pygame.color.Color('white')),) for t in new_lvl]
    
    if i > 2: n = 2
    else: n = i
    
    new_lvl[n + 1] = (font.render(f' #{i + 1} ', True, pygame.color.Color('black')), None, 'white')
        
    if len(lvl) >= 5 and i >= 2:
        new_lvl.extend([(font.render(str(lvl[u][0]), True, pygame.color.Color('white')),) for u in range(i - 2, i)])
        new_lvl.append((font.render(str(lvl[i][0]), True, pygame.color.Color('black')), None, 'white'))
        new_lvl.extend([(font.render(str(lvl[u][0]), True, pygame.color.Color('white')),) for u in range(i + 1, i + 3)])
        new_lvl.append((font.render(' Время', True, pygame.color.Color('white')),))
        new_lvl.extend([(font.render(f'{lvl[u][1] // 1000 // 60}:{lvl[u][1] // 1000 % 60}:{str(lvl[u][1] % 1000)[:2]}', True, pygame.color.Color('white')),) for u in range(i - 2, i)])
        new_lvl.append((font.render(f'{lvl[i][1] // 1000 // 60}:{lvl[i][1] // 1000 % 60}:{str(lvl[i][1] % 1000)[:2]}', True, pygame.color.Color('black')), None, 'white'))
        new_lvl.extend([(font.render(f'{lvl[u][1] // 1000 // 60}:{lvl[u][1] // 1000 % 60}:{str(lvl[u][1] % 1000)[:2]}', True, pygame.color.Color('white')),) for u in range(i + 1, i + 3)])
    
    elif len(lvl) >= 5:
        new_lvl.extend([(font.render(str(lvl[u][0]), True, pygame.color.Color('white')),) for u in range(0, i)])
        new_lvl.append((font.render(str(lvl[i][0]), True, pygame.color.Color('black')), None, 'white'))
        new_lvl.extend([(font.render(str(lvl[u][0]), True, pygame.color.Color('white')),) for u in range(i + 1, 5)])
        new_lvl.append((font.render(' Время', True, pygame.color.Color('white')),))
        new_lvl.extend([(font.render(f'{lvl[u][1] // 1000 // 60}:{lvl[u][1] // 1000 % 60}:{str(lvl[u][1] % 1000)[:2]}', True, pygame.color.Color('white')),) for u in range(0, i)])
        new_lvl.append((font.render(f'{lvl[i][1] // 1000 // 60}:{lvl[i][1] // 1000 % 60}:{str(lvl[i][1] % 1000)[:2]}', True, pygame.color.Color('black')), None, 'white'))
        new_lvl.extend([(font.render(f'{lvl[u][1] // 1000 // 60}:{lvl[u][1] // 1000 % 60}:{str(lvl[u][1] % 1000)[:2]}', True, pygame.color.Color('white')),) for u in range(i + 1, 5)])
    
    else:
        new_lvl.extend([(font.render(str(lvl[u][0]), True, pygame.color.Color('white')),) for u in range(0, i)])
        new_lvl.append([font.render(str(lvl[i][0]), True, pygame.color.Color('black')), None, 'white'])
        new_lvl.extend([(font.render(' -                   ', True, pygame.color.Color('white')),) for _ in range(12 - len(new_lvl))])
        new_lvl.append((font.render(' Время', True, pygame.color.Color('white')),))
        new_lvl.extend([(font.render(f'{lvl[u][1] // 1000 // 60}:{lvl[u][1] // 1000 % 60}:{str(lvl[u][1] % 1000)[:2]}', True, pygame.color.Color('white')),) for u in range(0, i)])
        new_lvl.append([font.render(f'{lvl[i][1] // 1000 // 60}:{lvl[i][1] // 1000 % 60}:{str(lvl[i][1] % 1000)[:2]}', True, pygame.color.Color('black')), None, 'white'])
        new_lvl.extend([(font.render(' -                   ', True, pygame.color.Color('white')),) for _ in range(18 - len(new_lvl))])

    lvl_tabl = classes.Menu.Table.Table(x + width // 2, y + height // 2.5, new_lvl, 3, border=1)
    
    txt = ['Выйти', 'Играть снова']
    data = [(x + width // 3 * (i * 1 + 1), y + height // 8 * 7, signal + i + 1, txt[i], (width // 4 , height // 9)) for i in range(2)]
    end_buttons = create_buttons_group(data, text=True, text_color='white', background_color='black', border=4)

    end_buttons.add(result)
    end_buttons.add(lvl_tabl)

    return end_buttons
    
    
def end_menu(screen, background, time, score, win, lvl):
    pygame.mouse.set_visible(True)

    width = screen.get_width()
    height = screen.get_height() // 9 * 7
    x = 0
    signal = pygame.USEREVENT
    end_buttons = create_end_menu(x, height // 9, width, height, signal, time, score, win, lvl)

    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                end_buttons.update(event.pos, False)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                end_buttons.update(event.pos, True)

            if event.type == pygame.USEREVENT + 1:
                running = False
                
            elif event.type == pygame.USEREVENT + 2:
                running = False
                game(screen, str(lvl))

        screen.fill(pygame.color.Color('black'))
        background.draw(screen)
        end_buttons.draw(screen)
        pygame.display.flip()
        

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    main_menu(screen)
    pygame.quit()


if __name__ == '__main__':
    main()
    