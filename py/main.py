import pygame
import classes


def main():
    pygame.init()
    size = 1000, 1000
    screen = pygame.display.set_mode(size)

    clock = pygame.time.Clock()

    player_group = pygame.sprite.Group()
    enemy_group = classes.Enemy_Group()
    player_bullet_group = pygame.sprite.Group()
    enemy_bullet_group = pygame.sprite.Group()

    player = classes.Player_SpaceShip1(100, 100, (0, 0, *size), player_bullet_group, enemy_group)

    player_group.add(player)
    player_group.draw(screen)

    for i in range(1, 4):
        enemy = classes.Enemy1(250 * i, 50, (0, 0, *size), enemy_bullet_group, player_group)
        enemy.bullet_group = enemy_bullet_group
        enemy_group.add(enemy)

    keys = {'up': False, 'down': False, 'left': False, 'right': False, 'shoot': False}

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    keys['up'] = True
                
                elif event.key == pygame.K_DOWN:
                    keys['down'] = True

                elif event.key == pygame.K_LEFT:
                    keys['left'] = True
                
                elif event.key == pygame.K_RIGHT:
                    keys['right'] = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    keys['up'] = False
                
                elif event.key == pygame.K_DOWN:
                    keys['down'] = False

                elif event.key == pygame.K_LEFT:
                    keys['left'] = False
                
                elif event.key == pygame.K_RIGHT:
                    keys['right'] = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                keys['shoot'] = True

            elif event.type == pygame.MOUSEBUTTONUP:
                keys['shoot'] = False

            elif event.type == pygame.QUIT:
                running = False

        if keys['up']: player.move(0, -1)
        if keys['down']: player.move(0, 1)
        if keys['left']: player.move(-1, 0)
        if keys['right']: player.move(1, 0)
        if keys['shoot']: player.shoot()
        
        screen.fill(pygame.Color('black'))
        player_group.draw(screen)
        enemy_group.update()
        enemy_group.draw(screen)
        player_bullet_group.update()
        enemy_bullet_group.update()
        player_bullet_group.draw(screen)
        enemy_bullet_group.draw(screen)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()