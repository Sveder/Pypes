"""
A class that builds a menu and handles inputs to it.
"""

import ConfigParser

import pygame
from pygame.locals import *

import data

DEFAULT_FONT = "SF Arch Rival v1.0\SF Arch Rival.ttf"
FONT_SIZE = 40

INI_HUD_SECTION = "hud"

class MenuItem:
    """
    A menu item that will appear as a line of text. Has a callback method
    associated with it.
    """
    def __init__(self, text, x, y, color, callback, size = FONT_SIZE, font = DEFAULT_FONT):
        """
        Defines a menu item.
        Input:
            text - The text that the menu item shows.
            x, y - The location of the menu item.
            callback - The callback to call when the item is clicked.
            font - The font to show the text in.
            color - The color of the font.
        """
        try:
            self.size = size
            self.text = text
            self.color = color
            self.callback = callback
            
            self.font = font
            #Create the font surface:
            font_obj = pygame.font.Font(data.filepath(self.font), size)
            self.sur_font = font_obj.render(self.text, True, self.color)
            self.sur_rect = pygame.Rect(x, y, self.sur_font.get_rect().width, self.sur_font.get_rect().height)

        except Exception , error:
            error = "Initializing the MenuItem class failed:\n %s" % (error)
            raise
        
    def call(self):
        self.callback()

    def check_point(self, (x, y)):
        """
        Checks if the point represented by (x,y) is in the area of the menu item.
        """
        if (x > self.sur_rect.left) and (x < self.sur_rect.right):
            if (y < self.sur_rect.bottom) and (y > self.sur_rect.top):
                return True
            
        return False


class StartMenu:
    """
    Shows a menu on the given screen using the MenuItems given.
    """
    def __init__(self, screen, items_list):
        """
        Initialize the class.
        Input:
            screen - The screen to blit on.
            items_list - A list of MenuItem-s to show.
        """
        try:
            self.screen = screen
            self.items_list = items_list
        except Exception , error:
            error = "Initializing the StartMenu class failed:\n %s" % (error)
            raise

    def start_menu(self):
        """
        Start the menu loop which waits for a click on a menu items, and calls
        its callback.
        """
        try:
            #First show all the menus on the screen:
            for item in self.items_list:
                self.screen.blit(item.sur_font, item.sur_rect)
                
            pygame.display.flip()
            
            self.chosen_item = None
            self.should_run = True
            while self.should_run:
                for event in pygame.event.get():
                    self.out_of_click_area = True
                    
                    if ((QUIT == event.type) or ((KEYDOWN == event.type) and (K_ESCAPE == event.key))):
                        self.should_run = False
                    elif ((KEYDOWN == event.type) and (K_F4 == event.key) and (4352 == event.mod)):
                        pygame.event.post(pygame.event.Event(QUIT))
                        
                    for item in self.items_list:
                        if (MOUSEBUTTONDOWN == event.type) and (item.check_point(event.pos)):
                            #And the mouse was clicked, end the loop and
                            #set the clicked item the current item.
                            self.chosen_item = item
                            self.should_run = False
                        elif (MOUSEMOTION == event.type) and (item.check_point(event.pos)):
                            self.out_of_click_area = False
                            if pygame.cursors.broken_x != pygame.mouse.get_cursor():
                                pygame.mouse.set_cursor(*pygame.cursors.broken_x)
                                
                    if (MOUSEMOTION == event.type) and (self.out_of_click_area) and (pygame.cursors.broken_x == pygame.mouse.get_cursor()):
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                                
            if None != self.chosen_item:
                self.chosen_item.call()

        except Exception , error:
            error = "start_menu in the StartMenu class failed:\n %s" % (error)
            raise

class HUDPart:
    """
    A hud region, containing the region and a callback to call if it's clicked.
    """
    def __init__(self, hot_spot_rect, callback):
        """
        Initializes the class with it's rectangle and he callback to use when
        clicked on.
        """
        self.hot_spot_rect = hot_spot_rect
        self.callback = callback
        
    def call(self):
        """
        Call the callback function.
        """
        self.callback()
        
    def check_point(self, (x, y)):
        """
        Checks if the point represented by (x,y) is in the area of the HUD item.
        """
        if (x > self.hot_spot_rect.left) and (x < self.hot_spot_rect.right):
            if (y < self.hot_spot_rect.bottom) and (y > self.hot_spot_rect.top):
                return True
            
        return False
    
class HUD:
    """
    The HUD (Heads Up Display) that will appear on the game board. The HUD will
    show the current image, the menu button, the money the player has got and
    buld options.
    """
    def __init__(self, location_rect, hud_ini, hud_parts=[]):
        """
        Initialize the hud using the location_rect location using hud_ini for
        all the images/sizes.
        """
        try:
            self.parts = hud_parts
            self.location_rect = location_rect
            self._parse_ini_file(hud_ini)
            self.sur_hud, rect = data.load_image(data.filepath(self.options["hud_bg"]))
            self.sur_rect = pygame.Rect(location_rect.x, location_rect.y, rect.height, rect.width)
            
        except Exception , error:
            error = "Initializing the HUD class failed:\n %s" % (error)
            raise
    
    def add_part(self, part):
        """
        Add the given part into the the part list.
        """
        self.parts.append(part)
        
    def _parse_ini_file(self, ini_file):
        """
        Parse the hud's ini file for all the important attributes:
        size
        """
        try:
            #Open the given ini file and read it:
            ini_parser = ConfigParser.ConfigParser()
            ini_parser.read(ini_file)
            #Read the screen options:
            self.options = dict(ini_parser.items(INI_HUD_SECTION))
            
        except Exception , error:
            error = "_parse_ini_file in the HUD class failed:\n %s" % (error)
            raise
    
    def handle_input(self, event):
        """
        Check if the event needs to be handled by the gui.
        """
        try:
            out_of_click_area = True
            
            if (MOUSEMOTION == event.type) and (700 < event.pos[0]):
                for part in self.parts:
                    if part.check_point(event.pos):
                        out_of_click_area = False
                        if pygame.cursors.broken_x != pygame.mouse.get_cursor():
                            pygame.mouse.set_cursor(*pygame.cursors.broken_x)
                        
            if (out_of_click_area) and (pygame.cursors.broken_x == pygame.mouse.get_cursor()):
                pygame.mouse.set_cursor(*pygame.cursors.arrow)
                    
            if (MOUSEBUTTONDOWN == event.type) and (700 < event.pos[0]):
                for part in self.parts:
                    if part.check_point(event.pos):
                        part.call()
                
                
        except Exception , error:
            error = "handle_input in the HUD class failed:\n %s" % (error)
            raise