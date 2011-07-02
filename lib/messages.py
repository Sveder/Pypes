"""
Message Poper
Michael Sverdlin 08.09.06
"""
#------------------------------IMPORTS-----------------------------------------#

import os
import sys
import random

import pygame
from pygame.colordict import THECOLORS as COLORS

import data
import main

#------------------------------GLOBALS-----------------------------------------#

#------------------------------CLASSES-----------------------------------------#

class Message:
    """
    Represents a class of a message popping into the users screen for a few
    seconds. It has 2 lines to write on, an pretty stuff all over it.
    """
    
    def __init__(self, first_line, second_line, options):
        self.options = options
        self.first_line = first_line
        self.second_line = second_line
        self.font_size = int(self.options["font_size"])
        try:
            self.font = pygame.font.Font(data.filepath(self.options["font"]), self.font_size)
        except IOError:
            self.font = pygame.font.SysFont(pygame.font.get_default_font(), self.font_size)
        
        self.rect = main.ini_list_to_rect(self.options["rect"])
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        #self.surface = pygame.image.load(data.filepath(self.options["image"])).convert()
        self.surface.set_colorkey(COLORS["black"])
        
        for index, letter in enumerate(first_line):
            self.draw_letter(index, letter, 0)
        
        for index, letter in enumerate(second_line):
            self.draw_letter(index, letter, 1)
        
    def draw_letter(self, index, letter, line = 0):
        letter_surface = self.font.render(letter, True, random.choice(COLORS.values()))
        letter_x = self.font_size / 2 * index
        if letter in ['i', 'l', '1', ')']:
            letter_x += 5
        
        elif letter in ['(']:
            letter_x += 10
        
        target_rect = pygame.locals.Rect(letter_x, (letter_surface.get_rect().height + 5) * line , letter_surface.get_rect().width, letter_surface.get_rect().height)
        self.surface.blit(letter_surface, target_rect)

#------------------------------FUNCTIONS---------------------------------------#