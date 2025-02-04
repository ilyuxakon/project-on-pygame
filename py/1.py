import pygame
import classes
import sqlite3

con = sqlite3.connect('levels\\record.sqlite')
cur = con.cursor()
cur.execute('INSERT INTO record VALUES(1, 2, 3)')
con.commit()

pygame.init()
screen = pygame.display.set_mode((800, 800))

data = ((pygame.image.load('data\image\player\cannon\zapper\Main Ship - Zapper Base.png',),), (pygame.image.load('data\image\player\cannon\zapper\Main ship weapon - Projectile - Zapper.png'),), (pygame.image.load('data\image\player\cannon\zapper\Main ship weapon - Projectile - Zapper.png'),), (pygame.image.load('data\image\player\cannon\zapper\Main ship weapon - Projectile - Zapper.png'),))
table = classes.Menu.Table.Table(400, 100, data, 2, 3, header=(pygame.image.load('data\image\other\icons8-замок-150.png'),))
t = pygame.sprite.Group()
t.add(table)
t.draw(screen)
pygame.display.flip()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

