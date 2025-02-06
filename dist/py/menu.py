import pygame
import pygame.scrap
import animations


class BackGround(pygame.sprite.Sprite):  # класс фона
    
    def __init__(self, group, width, height, earth, x, y):
        super().__init__()
        
        bg1 = animations.make_frames('data\image\other\\background\Starry background  - Layer 01 - Void.png', 9, 1)
        bg2 = animations.make_frames('data\image\other\\background\Starry background  - Layer 02 - Stars.png', 9, 1)
        
        earth = animations.make_frames('data\image\other\\background\Earth-Like planet.png', 77, 1)
        self.x, self.y = x, y
        self.earth_frames = earth
        self.earth_current_frames = 0
        self.earth_check = earth
        
        rect = bg1[0].get_rect()
        
        self.background_frames = []
        
        for i in range(len(bg1)):
            bg = bg1[i]
            bg.blit(bg2[i], (0, 0))
            background = pygame.surface.Surface((width, height))
            
            # дублирует изображение фона по обоим осям, чтобы полностью заполнить экран
            for x in range(width // rect.width + 1):
                for y in range(height // rect.height + 1):
                    background.blit(bg, (x * rect.width, y * rect.height))     
            
            self.background_frames.append(background)
            
        self.background_current_frames = 0
        self.image = self.background_frames[self.background_current_frames].copy()
        
        if self.earth_frames:
            self.image.blit(self.earth_frames[self.earth_current_frames], (self.x, self.y))
            
        self.rect = self.image.get_rect()
        
        group.add(self)
    
    
    def earth(self):  # включает и выключает изображение земли
        self.earth_check = not self.earth_check
        
        
    def update(self):
        self.background_current_frames = (self.background_current_frames + 1) % len(self.background_frames)
        self.image = self.background_frames[self.background_current_frames].copy()
        
        if self.earth_check:
            self.earth_current_frames = (self.earth_current_frames + 1) % len(self.earth_frames)
            self.image.blit(self.earth_frames[self.earth_current_frames], (self.x, self.y))


class Menu():
    
    class Button():
        
        class Button(pygame.sprite.Sprite):  # класс кнопки

            def __init__(self, x, y, signal, image, size, text=False, text_color='black', background_color=None, background=None, border=0, border_color='white'):
                super().__init__()
                
                self.event = pygame.event.Event(signal)

                # собирает изображение кнопки
                if text:
                    font = pygame.font.Font(None, int(size[0] * 0.2))
                    self.main_image = font.render(image, True, pygame.color.Color(text_color))

                else:
                    self.main_image = image
                    
                self.main_image_rect = self.main_image.get_rect()

                self.original_image = pygame.surface.Surface(size, pygame.SRCALPHA)
                if background is not None:
                    self.original_image.blit(pygame.image.load(background), (0, 0))

                else:
                    if background_color is not None:
                        self.original_image.fill(pygame.color.Color(background_color))
                self.rect = self.original_image.get_rect()

                self.original_image.blit(self.main_image, ((self.rect.width - self.main_image_rect.width) // 2, (self.rect.height - self.main_image_rect.height) // 2))

                if border != 0:
                    pygame.draw.lines(self.original_image, pygame.color.Color(border_color), True, ((border // 2, border // 2), (size[0] - border // 2 - 1 , border // 2), (size[0] - border // 2 - 1, size[1] - border // 2 - 1), (border // 2, size[1] - border // 2 - 1)), border)
                self.image = self.original_image.copy()

                self.rect.centerx, self.rect.centery = x, y


            def switch(self, flag): 
                if flag:  # кнопка активна
                    self.image = self.original_image.copy()
                    self.image.set_alpha(128)

                else:  # кнопка неактивна
                    self.image = self.original_image.copy()
            
            
            def click(self, flag):  # при нажатии создаёт сигнал
                if flag:
                    pygame.event.post(self.event)


            def actively(self, coord):  # проверяет находится ли курсо на кнопки
                return self.rect.x <= coord[0] <= self.rect.right and\
                    self.rect.y <= coord[1] <= self.rect.bottom


            def work(self, coord, click):  # управляет работой кнопки
                flag = self.actively(coord)
                
                if click:
                    self.click(flag)

                else:
                    self.switch(flag)
                    
                return flag


        class Button_Group(pygame.sprite.Group):  # группа кнопок
            
            def __init__(self):
                super().__init__()
                self.dict = dict()
                
                
            def update(self, coord, click):
                for sprite in self.sprites():
                    if type(sprite) == Menu.Button.Button:
                        sprite.work(coord, click)

                    elif type(sprite) == Menu.Button.Switch_Button_Group:
                        sprite.update(coord, click)

                    else:
                        sprite.update()


        class Switch_Button_Group(Button_Group):  # группа кнопок с постоянно нажатой одной кнопкой
        
            def __init__(self, button_group, n):
                super().__init__()
                
                # создаётся из класса Button_Group
                self.dict = button_group.dict
                self.spritedict = button_group.spritedict
                i = -1
                
                # активирует "нажатую" кнопку
                for sprite in self.sprites():
                    if type(sprite) == Menu.Button.Button:
                        i += 1
                        if i == n:
                            self.current_active_sprite = sprite
                            self.current_active_sprite.switch(True)


            def update(self, coord, click):
                for sprite in self.sprites():
                    if type(sprite) == Menu.Button.Button and click:
                        if sprite.actively(coord): # выключает старую и включает новую кнопку
                            self.current_active_sprite.switch(False)
                            self.current_active_sprite = sprite
                            self.current_active_sprite.switch(True)
                            self.current_active_sprite.click(True)

                    else:
                        sprite.update()

    
    class Group_Group():  # группа обрабатывающая другие группы
        
        def __init__(self):
            self.list = list()
            self.dict = dict()


        def add(self, group):
            self.list.append(group)


        def draw(self, screen):
            for group in self.list:
                group.draw(screen)


        def update(self, coord, click):
            for group in self.list:
                group.update(coord, click)


    class Data():
        
        class Image(pygame.sprite.Sprite):  # класс изображений
            
            def __init__(self, x, y, images):
                super().__init__()
                new_images = list()

                # создаёт список изображений которые могут выводиться
                for im in images:
                    rect = im.get_rect()
                    image = pygame.surface.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    image.blit(im, (0, 0))
                    new_images.append(image)

                self.images = new_images
                self.current_image = 0
                self.image = self.images[self.current_image]
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.centery = self.x, self.y = x, y


            def next(self):  # следующее изображение
                self.current_image = (self.current_image + 1) % len(self.images)
                self.image = self.images[self.current_image]
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.centery = self.x, self.y


            def previous(self):  # предыдущее изображение
                self.current_image = (self.current_image - 1) % len(self.images)
                self.image = self.images[self.current_image]
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.centery = self.x, self.y


            def set_alpha(self, n):  # изменяет прозрачность текущего изображения
                self.image.set_alpha(n)


        class Text(pygame.sprite.Sprite):  # класс текстов

            def __init__(self, x, y, height, texts, color):
                super().__init__()
                images = []
                font = pygame.font.Font(None, height)
                
                # создаёт список текстов которые могут выводиться
                for text in texts:
                    text = font.render(text, True, pygame.color.Color(color))
                    rect = text.get_rect()
                    image = pygame.surface.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    image.blit(text, (0, 0))
                    images.append(image)

                self.images = images
                self.current_image = 0
                self.image = self.images[self.current_image]
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.centery = self.x, self.y = x, y


            def next(self):  # следующий текст
                self.current_image = (self.current_image + 1) % len(self.images)
                self.image = self.images[self.current_image]
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.centery = self.x, self.y


            def previous(self):  # предыдущий текст
                self.current_image = (self.current_image - 1) % len(self.images)
                self.image = self.images[self.current_image]
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.centery = self.x, self.y


            def set_alpha(self, n):  # изменяет прозрачность текущего текста
                self.image.set_alpha(n)


        class Empty(pygame.sprite.Sprite):  # класс пустого пространства

            def __init__(self, x, y, width, height):
                super().__init__()
                self.image = pygame.surface.Surface((width, height), pygame.SRCALPHA)
                self.image = self.image.convert_alpha()
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.centery = self.x, self.y = x, y


            def next(self):  # затычка
                pass


            def previous(self):  # затычка
                pass


            def set_alpha(self, n):  # затычка
                pass


        class Data(pygame.sprite.Group):  # класс данных выводит группы изображений и текстов

            def __init__(self, x, y, data, text_height, color, names, available):
                super().__init__()
                self.spriteslist = []
                self.names = names
                self.available = available
                height = 0
                
                for d in data:
                    if d[-1] == 1:
                        sprite = Menu.Data.Image(x, y, d[0])
                        self.spriteslist.append(sprite)
                        self.add(sprite)
                    
                    elif d[-1] == 2:
                        sprite = Menu.Data.Text(x, y, text_height, d[0], color)
                        self.spriteslist.append(sprite)
                        self.add(sprite)

                    elif d[-1] == 3:
                        sprite = Menu.Table.Tables(x, y, d[:-1])
                        self.spriteslist.append(sprite)
                        self.add(sprite)

                    elif d[-1] == 4:
                        sprite = Menu.Data.Empty(x, y, 1, d[0])
                        self.spriteslist.append(sprite)
                        self.add(sprite)

                    height += self.spriteslist[-1].rect.height

                self.height = height
                self.y = y
                self.vertical_alignment()

                # block_sprite выводится когда игрок смотрит недоступную страницу
                image1= pygame.image.load('data\\image\\other\\icons8-замок-150.png')
                self.block_sprite = pygame.sprite.Sprite()
                self.block_sprite.image = image1
                self.block_sprite.image.set_colorkey(pygame.color.Color('black'))
                self.block_sprite.rect = self.block_sprite.image.get_rect()
                self.block_sprite.rect.centerx, self.block_sprite.rect.centery = x, y
                self.block_sprite.image.set_alpha(0)

                self.add(self.block_sprite)


            def vertical_alignment(self):  # выравнивает все спрайты по высоте
                if len(self.spriteslist) > 1:
                    y = self.y
                    y -= self.height // 2
                    for sprite in self.spriteslist:
                        sprite.rect.centery = y + sprite.rect.height // 2
                        y += sprite.rect.height


            def set_available(self, available):  # изменяет количество доступных страниц
                self.available = available


            def next(self):  # следующая страница
                self.block_sprite.image.set_alpha(0)
                for sprite in self.spriteslist:
                    sprite.next()
                self.vertical_alignment()

                if self.spriteslist[0].current_image >= self.available:  # проверка доступна ли страница игроку
                    self.block()
                    return False
                
                else:
                    return True


            def previous(self):  # предыдущая страница
                self.block_sprite.image.set_alpha(0)
                for sprite in self.spriteslist:
                    sprite.previous()
                self.vertical_alignment()

                if self.spriteslist[0].current_image >= self.available:  # проверка доступна ли страница игроку
                    self.block()
                    return False
                
                else:
                    return True
            
            
            def get_current_objectname(self):  # возвращает имя текущей страницы
                return self.names[self.spriteslist[0].current_image]
            
            
            def block(self):  # если игроку недоступна страница - делает её полупрозрачной и выводит замок(block_sprite)
                for sprite in self.spriteslist:
                    sprite.set_alpha(128)
                    self.block_sprite.image.set_alpha(256)


    class Table():            

        class Tables(pygame.sprite.Sprite):  # класс таблиц

            def __init__(self, x, y, tables):
                super().__init__()
                new_images = list()

                # создаёт список таблиц
                for tb in tables:
                    table = Menu.Table.Table(0, 0, *tb)
                    image = pygame.surface.Surface((table.rect.width, table.rect.height), pygame.SRCALPHA)
                    image.blit(table.image, (0, 0))
                    new_images.append(image)

                self.images = new_images
                self.current_image = 0
                self.image = self.images[self.current_image]
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.centery = self.x, self.y = x, y


            def next(self):  # следующая таблица
                self.current_image = (self.current_image + 1) % len(self.images)
                self.image = self.images[self.current_image].copy()
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.centery = self.x, self.y
           
                 
            def previous(self):  # предыдущая таблица
                self.current_image = (self.current_image - 1) % len(self.images)
                self.image = self.images[self.current_image]
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.centery = self.x, self.y


            def set_alpha(self, n):  # устанаваливает прозрачность текущей таблицы
                self.image.set_alpha(n)


        class Table(pygame.sprite.Sprite):  # класс таблицы
            
            def __init__(self, x, y, cells, columns_count, border=0, border_color='white', header=None):
                super().__init__()
                self.x, self.y = x, y
                self.border = border

                # создаёт столбцы
                self.columns = [Menu.Table.Column(0, 0, cells[i * len(cells) // columns_count:(i + 1) * len(cells) // columns_count], border, border_color) for i in range(columns_count)]
                
                # заголовок
                if header is not None: self.header = Menu.Table.Cell(*header, border=border, border_color=border_color)
                else: self.header = False

                self.update_width()
                self.update_height()
                self.make_table()


            def update_width(self):  # получает ширину таблицы
                self.width = sum(column.width for column in self.columns) - (len(self.columns) - 1) * self.border


            def update_height(self):  # получает высоту для каждой строки
                self.heights = list()
                
                for i in range(len(self.columns[0].cells)):
                    self.heights.append(max(column.cells[i].rect.height for column in self.columns))


            def make_table(self):  # создаёт таблицу
                x = 0

                if self.header:  # заголовок
                    self.header.make_cell(self.width, self.header.rect.height)
                    self.header.rect.x, self.header.rect.y = x, 0
                    y = 0 + self.header.rect.height - self.header.border[0]

                else: y = 0

                for column in self.columns: 
                    column.set_cells_size(self.heights, x_0=x, y_0=y)  # в каждом столбце изменяет высоту ячейки на высоту строки
                    column.alignment()
                    x += column.width - self.border

                if self.header: height = sum(self.heights) + self.header.rect.height - len(self.heights) * self.border
                else: height = sum(self.heights) - (len(self.heights) - 1) * self.border

                surface = pygame.surface.Surface((self.width + self.border, height))
                surface.set_colorkey(pygame.color.Color('black'))

                # выводит все ячейки на один surface
                if self.header: surface.blit(self.header.image, (0, 0))

                for column in self.columns:
                    for cell in column.cells:
                        surface.blit(cell.image, (cell.rect.x, cell.rect.y))
                
                self.image = surface
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.y = self.x, self.y


        class Column(pygame.sprite.Group):  # класс столбца таблицы
            
            def __init__(self, x_0, y_0, cells, border=0, border_color='white'):
                self.x_0, self.y_0 = x_0, y_0
                self.border = border

                self.cells = list()
                self.cells_heights = list()

                # создаёт ячейки в столбце
                for cell in cells:
                    cell = Menu.Table.Cell(*cell, border=border, border_color=border_color)
                    self.cells.append(cell)
                    self.cells_heights.append(self.cells[-1].rect.height)

                self.width = max([cell.rect.width for cell in self.cells]) # ширина столбца равна максимальной ширине ячейки


            def set_cells_size(self, cells_heights, x_0=None, y_0=None):  # меняет размер ячеек
                self.cells_heights = cells_heights

                if x_0 is not None: self.x_0 = x_0
                if y_0 is not None: self.y_0 = y_0

                self.alignment()


            def alignment(self):  # выравнивает ячейки по высоте
                y = self.y_0

                for i in range(len(self.cells)):
                    self.cells[i].make_cell(self.width, self.cells_heights[i])
                    self.cells[i].rect.x = self.x_0
                    self.cells[i].rect.y = y

                    y += (self.cells[i].rect.height - self.border)


        class Cell():  # класс ячейки таблицы

            def __init__(self, image, background=None, background_color=None, border=0, border_color='white'):
                if type(image) == pygame.surface.Surface:
                    self.original_image = image
                    
                else:
                    self.original_image = image.image

                self.background = (background, background_color)
                self.border = (border, border_color)

                self.make_cell(*self.get_rect())


            def make_cell(self, width, height):  # создаёт ячейку нужных размеров
                surface = pygame.surface.Surface((width, height), pygame.SRCALPHA)
                
                if self.background[0] is None:
                    if self.background[1] is not None:
                        surface.fill(pygame.color.Color(self.background[1]))
                        
                    else:
                        surface.set_colorkey(pygame.color.Color('black'))
                
                else:
                    rect = self.background[0].get_rect()
                    background = self.background[0].copy

                    if rect.width > width and rect.height > height:
                        x, y = (rect.width - (width - self.border * 2)) // 2, (rect.height - (height - self.border * 2)) // 2
                    
                    elif rect.width == width and rect.height == height:
                        x, y = 0, 0

                    else:
                        if rect.width < width:
                            background = pygame.transform.scale(background, (width - self.border * 2, rect.height))
                            rect = background.get_rect()
                        
                        if rect.height < height:
                            background = pygame.transform.scale(background, (rect.width, height - self.border * 2))

                        x, y = 0, 0

                    surface.blit(background, (x, y))

                if self.border[0] != 0:
                    pygame.draw.lines(surface, pygame.color.Color(self.border[1]), True, ((self.border[0] // 2, self.border[0] // 2), (width - self.border[0] // 2 - 1, self.border[0] // 2), (width - self.border[0] // 2 - 1, height - self.border[0] // 2 - 1), (self.border[0] // 2, height - self.border[0] // 2 - 1)), self.border[0])

                rect = self.original_image.get_rect()
                surface.blit(self.original_image, ((width - rect.width) // 2, (height - rect.height) // 2))
                self.image = surface
                self.rect = self.image.get_rect()


            def get_rect(self):  # возвращает размер ячейки
                rect = self.original_image.get_rect()
                return rect.width + self.border[0] * 2, rect.height + self.border[0] * 2
    