import pygame 

def make_frames(sheet, columns, rows, cannon=False):
    columns, rows = int(columns), int(rows)
    sheet = pygame.image.load(sheet)
    frames = []
    rect = pygame.Rect(0, 0, sheet.get_width() // columns, 
                            sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (rect.w * i, rect.h * j)
            frames.append(sheet.subsurface(pygame.Rect(
                frame_location, rect.size)))
    
    new_frames = []
    for frame in frames:
        if cannon:
            new_frames.append(frame)
    
        else:
            new_frames.append(frame)
            new_frames.append(frame)
            new_frames.append(frame)
            new_frames.append(frame)
            new_frames.append(frame)
            new_frames.append(frame)
            new_frames.append(frame)
            new_frames.append(frame)


    return(new_frames)

if __name__ == '__main__':
    cannon = make_frames()
    pygame.init()
    screen = pygame.display.set_mode((300, 300))
    screen.blit(cannon[0], (20, 20))
    clock = pygame.time.Clock()
    while True:
        for i in range(7):
            screen.fill(pygame.Color('black'))
            screen.blit(cannon[i], (20, 20))
            pygame.display.flip()
            clock.tick(10)


