import pygame
import get_settings
import classes


def hud_update(heart, health_bar, surface):
    pass

def create_lvl2():
    lvl = get_settings.create_lvl()

    if lvl[1] == 'auto_cannon': lvl.insert(1, classes.Auto_Cannon)
    elif lvl[1] == 'big_space_cannon': lvl.insert(1, classes.Big_Space_Cannon)

    if lvl[3] == 'base_engine': lvl.insert(3, classes.Base_Engine)

    return lvl

def game(screen):
    lvl = create_lvl2()

    spaceships_group = classes.Spaceship_Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    player_bullet_group = pygame.sprite.Group()
    enemy_bullet_group = pygame.sprite.Group()

    player = classes.Player_SpaceShip(300, 700, (0, 0, 1000, 1000), spaceships_group, player_bullet_group, enemy_group, player_group, *lvl)

    enemy = classes.Enemy_Fighter(300, 200, (0, 0, 1000, 1000), spaceships_group, enemy_bullet_group, player_group, enemy_group)

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
        player_bullet_group.update()
        enemy_bullet_group.update()
        player_bullet_group.draw(screen)
        enemy_bullet_group.draw(screen)
        player_group.update()
        player_group.draw(screen)
        enemy_group.update()
        enemy_group.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 1000))
    game(screen)
    pygame.quit()

if __name__ == '__main__':
    main()