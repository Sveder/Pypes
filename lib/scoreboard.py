"""
The scoreboard class for pyweek 5...
"""
#------------------------------IMPORTS-----------------------------------------#

import os
import sys
import time

import pygame
from pygame.colordict import THECOLORS as COLORS

import data
import main

#------------------------------GLOBALS-----------------------------------------#

#------------------------------CLASSES-----------------------------------------#

class ScoreBoard:
    """
    First quadrant - Has the score and time left until the transmission starts.
    """
    def __init__(self, rect, options):
        """
        Init the class with data. Create the background.
        """
        self.rect = rect
        self.options = options
        
        
        self.score = 0
        self.surface = pygame.Surface((rect.width, rect.height))
        self.surface.set_colorkey(COLORS["black"])
        
        try:
            self.time_font = pygame.font.Font(data.filepath(self.options["time_font"]), int(self.options["time_font_size"]))            
        except IOError:
            self.time_font = pygame.font.SysFont(pygame.font.get_default_font(), int(self.options["time_font_size"]))
        
        try:
            self.score_font = pygame.font.Font(data.filepath(self.options["score_font"]), int(self.options["score_font_size"]))            
        except IOError:
            self.score_font = pygame.font.SysFont(pygame.font.get_default_font(), int(self.options["score_font_size"]))
    
    def show(self, seconds_left):
        """
        Show the score and the timer.
        """
        self.blit_bg()
        
        score_surface = self.score_font.render(str(self.score), True, COLORS["white"])
        self.surface.blit(score_surface, main.ini_list_to_rect(self.options["score_rect"]))
        
        time_string = time.strftime("%M:%S", time.localtime(seconds_left))
        time_surface = self.time_font.render(time_string, True, COLORS["white"])
        self.surface.blit(time_surface, main.ini_list_to_rect(self.options["time_rect"]))
    
    def blit_bg(self):
        """
        Blit the bg in some cool way.
        """
        self.surface.fill(COLORS["black"])