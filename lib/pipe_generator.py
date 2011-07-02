"""
The scoreboard class for pyweek 5...
"""
#------------------------------IMPORTS-----------------------------------------#

import os
import sys
import time
import random
random.seed()
import ConfigParser
import pygame
from pygame.colordict import THECOLORS as COLORS

import data
import main
import pipes

#------------------------------GLOBALS-----------------------------------------#

#------------------------------CLASSES-----------------------------------------#

class PipeGenerator:
    """
    This class contains the next pipes availibale to the player and to show that
    pipe.
    """
    
    def __init__(self, rect, options, pipe_config):
        self.rect = rect
        self.options = options
        
        self.pipes_options = ConfigParser.ConfigParser()
        self.pipes_options.read([pipe_config])
        
        self.surface = pygame.Surface((rect.width, rect.height))
        self.surface.set_colorkey(COLORS["black"])
        
        self.pipes_to_show = 5
        
        try:
            self.font = pygame.font.Font(data.filepath(self.options["font"]), int(self.options["font_size"]))            
        except IOError:
            self.font = pygame.font.SysFont(pygame.font.get_default_font(), int(self.options["font_size"]))
        
        next_surface = self.font.render("Next", True, COLORS["white"])
        tiles_surface = self.font.render("tiles:", True, COLORS["white"])
        
        self.surface.blit(next_surface, pygame.locals.Rect(30, 30, 0, 0))
        self.surface.blit(tiles_surface, pygame.locals.Rect(30, 70, 0, 0))
        
        self.next_pipes = self.generate_some_pipes()
        
    def get_next(self):
        """
        Get the next pipe.
        """
        ret_pipe = self.next_pipes[0]
        self.next_pipes = self.next_pipes[1:]
        
        if self.pipes_to_show >= len(self.next_pipes):
            self.next_pipes += self.generate_some_pipes()
        
        return ret_pipe
    
    def generate_some_pipes(self):
        """
        Generate some random pipes to fill up the world.
        """
        next_pipes = []
        for i in xrange(int(self.options["pipes_per_batch"])):
            type = random.choice([1, 1, 1, 2, 2])
            
            if 1 == type:
                #Straight chosen:
                cur_options = dict(self.pipes_options.items("StraightPipe"))
                cur_start_dir = random.choice(main.DIRECTIONS.LIST)
                while 1:
                    cur_exit_dir = random.choice(main.DIRECTIONS.LIST)
                    if cur_exit_dir != cur_start_dir:
                        break
                
                cur_image = os.path.join(os.path.dirname(cur_options["image"]), str(cur_start_dir) + "_" + str(cur_exit_dir) + "_" + os.path.basename(cur_options["image"]))
                if not os.path.isfile(data.filepath(cur_image)):
                    cur_image = os.path.join(os.path.dirname(cur_options["image"]), str(cur_exit_dir) + "_" + str(cur_start_dir) + "_" + os.path.basename(cur_options["image"]))
                
                cur_options["image"] = cur_image
                
                next_pipes.append(pipes.StraightPipe(cur_start_dir, cur_exit_dir, cur_options))
            
            if 2 == type:
                #+ chosen:
                cur_options = dict(self.pipes_options.items("PlusPipe"))
                next_pipes.append(pipes.PlusPipe(cur_options))
                    
        
        return next_pipes
    
    def show_pipes(self):
        """
        Show the first 5 pipes (next pipe first...).
        """
        for i in xrange(self.pipes_to_show):
            self.surface.blit(self.next_pipes[i].surface, pygame.locals.Rect(50, 150 + 65 * i, 50, 50))