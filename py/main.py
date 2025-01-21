import pygame
import get_settings
import classes


FPS = 60

def settings(lvl_name):
    player = get_settings.create_player_ship()

    if player[1] == 'auto_cannon': player.insert(1, classes.Auto_Cannon)
    elif player[1] == 'big_space_cannon': player.insert(1, classes.Big_Space_Cannon)

    if player[3] == 'base_engine': player.insert(3, classes.Base_Engine)

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
    spaceships_group = classes.Spaceship_Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    player_bullet_group = pygame.sprite.Group()
    enemy_bullet_group = pygame.sprite.Group()

    game_group = classes.Game_Group()
    game_group.add(player_bullet_group, player_group, enemy_bullet_group, enemy_group, hud_group)
    
    player = classes.Player_SpaceShip(400 + x, height * 0.75, (x, y + height // 2, x + 800, height), screen.get_width(), height, spaceships_group, player_bullet_group, enemy_group, player_group, *s[:-1], x + width + 20, 20, (screen.get_width() - width) // 2 - 44, 30, hud_group)

    wall1 = classes.Wall(x - 4, y, y + height, hud_group)
    wall2 = classes.Wall(x + 800, y, y + height, hud_group)

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
                enemy = classes.Enemy_Fighter(int(width * (pos_x + 0.5)) + x, int((pos_y + 0.5) * pos_height), (x, y + screen_height // 2, x + 800, screen_height), spaceships_group, enemy_bullet_group, player_group, enemy_group, screen_width, screen_height)

            elif placement[pos_y][pos_x] == 'fr':
                enemy = classes.Enemy_Frigate(int(width * (pos_x + 0.5)) + x, int((pos_y + 0.5) * pos_height), (x, y + screen_height // 2, x + 800, screen_height), spaceships_group, enemy_bullet_group, player_group, enemy_group, screen_width, screen_height)

            elif placement[pos_y][pos_x] == 'to':
                enemy = classes.Enemy_Torpedo(int(width * (pos_x + 0.5)) + x, int((pos_y + 0.5) * pos_height), (x, y + screen_height // 2, x + 800, screen_height), spaceships_group, enemy_bullet_group, player_group, enemy_group, screen_width, screen_height)


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

            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     keys['shoot'] = True

            # elif event.type == pygame.MOUSEBUTTONUP:
            #     keys['shoot1'] = False

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

    pygame.quit()

def main():
    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    game(screen)
    pygame.quit()

if __name__ == '__main__':
    main()