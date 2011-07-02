#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
#                               Pyweek5 - Pypes                                #
#                             -------------------                              #
#                                                                              #
#   Author:                                                                    #
#           Michael Sverdlin                                                   #
#   Date:                                                                      #
#           09.08                                                              #
#   Purpose:                                                                   #
#           A collection of possibale pipes for the game.                      #
#                                                                              # 
#   TODO:                                                                      #
#                                                                              #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
#------------------------------IMPORTS-----------------------------------------#

import os
import sys

import pygame

import data
import main
#------------------------------GLOBALS-----------------------------------------#

#------------------------------CLASSES-----------------------------------------#

class BasePipe:
    """
    A class for pipes to inherit from.
    """
    name = "BasePipe"
    def __init__(self, pipe_options = None):
        self.options = pipe_options
        self.is_enterable = False
        self.can_build_on = True
        self.e2e = {}
        
        if not pipe_options:
            #self.surface = pygame.image.load(data.filepath(os.path.join("pipe_images", "base_tile.tif"))).convert()
            self.surface = pygame.image.load(data.filepath(os.path.join("pipe_images", "base_tile.tif")))
            self.surface.set_colorkey(main.COLORS["white"])
            self.score = 0
            self.message = "I'm not a real pipe."
        
        else:
            #self.surface = pygame.image.load(data.filepath(self.options["image"])).convert()
            self.surface = pygame.image.load(data.filepath(self.options["image"]))
            self.score = int(self.options["score"])
            self.message = self.options["message"]
        
        self.chosen_start = -1
    
class StartPipe(BasePipe):
    """
    A pipe from which data starts.
    """
    def __init__(self, exit_direction, pipe_options):
        BasePipe.__init__(self, pipe_options)
        self.exit = int(exit_direction)
        self.e2e[1] = exit_direction
        self.e2e[2] = exit_direction
        self.e2e[3] = exit_direction
        self.e2e[4] = exit_direction
        self.can_build_on = False
        self.is_enterable = False

class StopPipe(BasePipe):
    """
    A pipe in which data end.
    """
    def __init__(self, entry_direction, pipe_options):
        BasePipe.__init__(self, pipe_options)
        self.e2e[entry_direction] = 1
        self.can_build_on = False
        self.is_enterable = True
        
class StraightPipe(BasePipe):
    """
    A 1 to 1 two way pipe.
    """
    name = "StraightPipe"
    def __init__(self, in_dir, out_dir, options):
        BasePipe.__init__(self, options)
        self.e2e = {in_dir : out_dir, out_dir : in_dir}
        self.is_enterable = True

class PlusPipe(BasePipe):
    name = "PlusPipe"
    def __init__(self, options):
        BasePipe.__init__(self, options)
        self.e2e = main.DIRECTIONS.OPPOSITES
        self.is_enterable = True
        self.noe = 0


#------------------------------FUNCTIONS---------------------------------------#

#Pipe types = OneToOne, Two to Two, Stucker, Delay, OneWay, Other
pipe_types = []
for i in xrange(20):
    pipe_types.append(StraightPipe)