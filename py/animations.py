import pygame 


def make_frames(sheet, columns, rows, cannon=False):
    if sheet == 'None':
        return None
    
    else:
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
                new_frames.append(frame)
                new_frames.append(frame)
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


def get_image(sheet, columns, rows):
    return make_frames(sheet, columns, rows)[0]
