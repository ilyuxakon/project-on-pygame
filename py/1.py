import animations
import pygame

a = input().split(';')
image = animations.make_frames(a[0], int(a[1]), int(a[2]))[0]
b = input()
pygame.image.save(image, b)
