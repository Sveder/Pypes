"""#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#                               Pypes                                          #
#                             ---------                                        #
#                                                                              #
#   Author:                                                                    #
#           Michael Sverdlin                                                   #
#   Date:                                                                      #
#           09.08                                                              #
#   Purpose:                                                                   #
#                                                                              # 
#   TODO:                                                                      #
#        FIX score alignment with time alignment (using spaces?)               #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#"""
#------------------------------IMPORTS-----------------------------------------#

import os
import sys
import time
import random
random.seed()
import ConfigParser

import pygame
from pygame.locals import *
from pygame.colordict import THECOLORS as COLORS
pygame.init()       #Initialize all of the pygame parts

import data
import menu
import pipes
import messages
from scoreboard import *
from pipe_generator import *

#------------------------------GLOBALS-----------------------------------------#

DEBUG = True
FULLSCREEN = 0

MAIN_INI_FILE = "game.ini"
INI_HUD_SECTION = "hud"
INI_GAME_SECTION = "game"
INI_NEXTS_SECTION = "nexts"
INI_GENERAL_SECTION = "general"
INI_MESSAGE_SECTION = "message"
INI_SCORE_BOARD_SECTION = "scoreboard"

THEME_FILE = "themes.ini"
THEME_GENERAL_SECTION = "general"
THEME_SECTION_PREFIX = "theme"
THEME_ALPHA = 45

MESSAGE_TIME = 1500

class DIRECTIONS:
    """
    Entry and exit direction, relative to the pipe you are ENTETING.
    """
    LEFT = 1
    UP = 2
    RIGHT = 3
    DOWN = 4
    
    OPPOSITES = {LEFT : RIGHT,
                 UP   : DOWN,
                 RIGHT: LEFT,
                 DOWN : UP}
    
    LIST = [1, 2, 3, 4]

class CUSTOM_EVENT:
    """
    User created events.
    """
    ADVANCE_TIMER = USEREVENT + 1
    TIME_BONUS = USEREVENT + 2
    MESSAGE_END = USEREVENT + 3
    STEP_FLOW = USEREVENT + 4
    
class STEP_RETURNS:
    """
    Return values of stepping in the the pipe path.
    """
    LOST = -1
    SAFE = 0
    WON = 1

class MENU_ITEMS:
    """
    A menu item return type...
    """
    HELP = 0
    PAUSE = 1
    EXIT = 2
    FF = 3
    
LEVEL_TIMES = [100, 90, 50, 30, 20, 10, 5, 4, 3, 2]
    
global g_twisted_bonus
g_twisted_bonus = False
#------------------------------CLASSES-----------------------------------------#

class Theme:
    def __init__(self, game_name, bg_image_path, intro_text, options):
        self.name = game_name
        self.intro_text = intro_text
        self.bg_image_sur = pygame.image.load(bg_image_path).convert()
        self.bg_image_sur.set_alpha(THEME_ALPHA)
        
        self.options = options
        self.score = int(self.options["score"])
        
class Level:
    def __init__(self, theme, time_left, level = 0):
        self.theme = theme
        self.level = level
        self.time_left = int(time_left)

class Game:
    """
    """

    def __init__(self, game_ini_path):
        """
        Initialize the game class.
        """
        try:
            self.levels_played = 0
            self.options = ConfigParser.ConfigParser()
            self.options.read([game_ini_path])
            
            self.message = None
            self.main_options = dict(self.options.items(INI_GENERAL_SECTION))
            
        except Exception , error:
            error = "Initializing the game class failed:\n %s" % (error)
            raise
    
    def load_themes(self):
        """
        Load all the theme info into a theme list.
        """
        self.themes_ini = ConfigParser.ConfigParser()
        self.themes_ini.read([data.filepath(THEME_FILE)])
        num_of_themes = self.themes_ini.getint(THEME_GENERAL_SECTION, "theme_count")
        
        self.themes = []
        for i in xrange(num_of_themes):
            cur_theme_options = dict(self.themes_ini.items(THEME_SECTION_PREFIX + "_" + str(i)))
            cur_theme = Theme(cur_theme_options["name"], data.filepath(cur_theme_options["bg"]), cur_theme_options["intro_text"], cur_theme_options)
            self.themes.append(cur_theme)
            
    def start(self):
        """
        Open the display.
        """
        if "true" == self.main_options["full_screen"]:
            FULLSCREEN = pygame.FULLSCREEN
        else:
            FULLSCREEN = 0
            
        self.screen = pygame.display.set_mode((int(self.main_options["screen_width"]), int(self.main_options["screen_height"])), FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Pypes!")
        
        self.load_themes()
        
        self.pause_surface, rect = data.load_image(data.filepath(self.main_options["pause_image"]))
        self.help_surface, rect = data.load_image(data.filepath(self.main_options["help_image"]))
        
        score_board_options = dict(self.options.items(INI_SCORE_BOARD_SECTION))
        self.score_board = ScoreBoard(ini_list_to_rect(self.main_options["score_board_rect"]), score_board_options)
        
        self.menu = Menu(ini_list_to_rect(self.main_options["hud_rect"]), dict(self.options.items(INI_HUD_SECTION)))
        
        self.wins = {STEP_RETURNS.WON : 0}
        
        self.intro()
        
        for i in xrange(int(self.main_options["max_levels"])):
            answer = self.start_level(i)
            #print "Game answer = ", answer
            if self.wins.has_key(answer):
                self.wins[answer] += 1
            else:
                self.wins[answer] = 1
            
            if 2 == answer:
                break
        
        self.exit()
    
    def intro(self):
        """
        Shows an intro screen.
        """
        sur = pygame.image.load(data.filepath(self.main_options["intro_screen"])).convert()
        self.show_pic(sur)
    
    def show_pic(self, surface):
        """
        Shows an image until the user presses a key.
        """
        intro = surface
        out = False
        while not out:
            for event in pygame.event.get():
                if (event.type in [MOUSEBUTTONDOWN, KEYDOWN, QUIT]):
                    out = True
            
            self.screen.blit(intro, (0,0,0,0))
            pygame.display.flip()
        
    def start_level(self, diff):
        """
        Start a level.
        """
        self.pipe_generator = PipeGenerator(ini_list_to_rect(self.main_options["nexts_rect"]),  dict(self.options.items(INI_NEXTS_SECTION)), data.filepath("pipes.ini"))
        
        level_time = LEVEL_TIMES[diff]
        self.level = Level(random.choice(self.themes), level_time)
        
        self.game_board = GridClass(self.options, self.score_board, self.pipe_generator, self.level, self)
        
        return self.main_game_loop()
    
    def main_game_loop(self):
        """
        This will feature the main game loop.
        """
        try:
            global g_twisted_bonus
            
            self.clock = pygame.time.Clock()
            self.is_flowing = False
            self.no_cheats = False
            self.ret = False
            self.paused = False
            self.step_time = 1500
            
            if pygame.cursors.arrow != pygame.mouse.get_cursor():
                pygame.mouse.set_cursor(*pygame.cursors.arrow)
            
            pygame.time.set_timer(CUSTOM_EVENT.ADVANCE_TIMER, 1000)
            self.score_board.show(self.level.time_left)
            self.pipe_generator.show_pipes()
            self.should_run = True
            
            self.time_bonus = 10 * 60 * 1000
            pygame.time.set_timer(CUSTOM_EVENT.TIME_BONUS, self.time_bonus)
            answer = None
            while self.should_run:                
                for event in pygame.event.get():
                    if (self.paused) and ((KEYDOWN == event.type) and ((event.key in [K_p, K_h])) or (MOUSEBUTTONDOWN == event.type)):
                        print "unpaused"
                        self.paused = False
                        continue
                    elif self.paused:
                        continue
                        
                    
                    #Check if we need to quit:
                    if QUIT == event.type:
                        return 2
                    #Quit if alt+f4 was hit:
                    elif ((KEYDOWN == event.type) and (K_F4 == event.key) and (4352 == event.mod)):
                        pygame.event.post(pygame.event.Event(QUIT))
                    
                    elif (KEYDOWN == event.type) and (K_l == event.key):
                        return 0
                    
                    #CHEAT CODES for time manipulations:
                    elif (KEYDOWN == event.type):
                        if not self.no_cheats:
                            if (K_KP_PLUS == event.key):
                                self.level.time_left += 5
                                pygame.event.post(pygame.event.Event(CUSTOM_EVENT.ADVANCE_TIMER))
                            elif (K_KP_MINUS == event.key):
                                self.level.time_left -= 5
                                pygame.event.post(pygame.event.Event(CUSTOM_EVENT.ADVANCE_TIMER))
                        
                        if (not self.paused) and (K_p == event.key):
                            self.pause()
                        
                        if (not self.paused) and (K_h == event.key):
                            self.help()
                        
                    #Update the score board:
                    elif CUSTOM_EVENT.ADVANCE_TIMER == event.type:
                        #Draw the score board:    
                        self.level.time_left -= 1
                        
                        #Start flow:
                        if (0 >= self.level.time_left) and (not self.is_flowing):
                            self.is_flowing = True
                            pygame.time.set_timer(CUSTOM_EVENT.ADVANCE_TIMER, 0)
                            self.level.time_left = 0
                            answer = self.game_board.start_flow()
                            self.no_cheats = True
                            pygame.time.set_timer(CUSTOM_EVENT.STEP_FLOW, self.step_time)
                    
                    #Put a tile:
                    elif (MOUSEBUTTONDOWN == event.type) and (1 == event.button) and (check_point(event.pos, self.game_board.rect) and (not self.game_board.is_done())):
                        self.game_board.handle_input(event)
                    
                    elif (MOUSEBUTTONDOWN == event.type) and check_point(event.pos, self.menu.rect):
                        menu_answer = self.menu.handle_input((event.pos[0], event.pos[1]))
                        if  MENU_ITEMS.PAUSE == menu_answer:
                            self.pause()
                            
                        elif MENU_ITEMS.HELP == menu_answer:
                            self.help()
                        
                        elif MENU_ITEMS.EXIT == menu_answer:
                           return 2
                        
                        elif MENU_ITEMS.FF == menu_answer:
                            self.ff()
                    
                    #Give time bonus:
                    elif (CUSTOM_EVENT.TIME_BONUS == event.type):
                        self.message = messages.Message("Bonus (%sm)" % (self.time_bonus / 1000 / 60), "1000", dict(self.options.items(INI_MESSAGE_SECTION)))
                        self.score_board.score += 1000
                        pygame.time.set_timer(CUSTOM_EVENT.MESSAGE_END, MESSAGE_TIME)
                        self.time_bonus *= 2
                    
                    #Remove current message:
                    elif (CUSTOM_EVENT.MESSAGE_END == event.type):
                        self.message = None
                        pygame.time.set_timer(CUSTOM_EVENT.MESSAGE_END, 0)
                        pygame.time.set_timer(CUSTOM_EVENT.TIME_BONUS, self.time_bonus)
                        if self.ret:
                            return answer
                    
                    #Step in the routing:
                    elif (CUSTOM_EVENT.STEP_FLOW == event.type):
                        answer = self.game_board.step_flow()
                
                if self.paused:
                    continue
                
                if None != answer:
                    if not STEP_RETURNS.SAFE == answer:
                        pygame.time.set_timer(CUSTOM_EVENT.STEP_FLOW, 0)
                        self.ret = True
                
                #Blit the scores:
                if 0 > self.level.time_left:
                    self.level.time_left = 0
                    
                if g_twisted_bonus:
                    self.twist_message = messages.Message("TWISTED BONUS!", "5000", dict(self.options.items(INI_MESSAGE_SECTION)))
                    self.message = self.twist_message
                    self.score_board.score += 5000
                    pygame.time.set_timer(CUSTOM_EVENT.MESSAGE_END, MESSAGE_TIME * 2)
                    g_twisted_bonus = False
                    
                    
                self.score_board.show(self.level.time_left)
                self.screen.blit(self.score_board.surface, self.score_board.rect)
                
                #Blit the game board:
                self.game_board.blit()
                self.screen.blit(self.game_board.surface, self.game_board.rect)
                
                #Blit the menu:
                self.screen.blit(self.menu.surface, self.menu.rect)
                
                #Blit the bg of the theme:
                self.screen.blit(self.level.theme.bg_image_sur, Rect(0, 0, 600, 800))                
                
                self.pipe_generator.show_pipes()
                self.screen.blit(self.pipe_generator.surface, self.pipe_generator.rect)

                if self.message:
                    self.screen.blit(self.message.surface, self.message.rect)
                
                pygame.display.update()
                self.clock.tick(100)
                #self.clock.get_fps()

        except Exception , error:
            error = "_main_game_loop in the game class failed:\n %s" % (error)
            raise
        
    def ff(self):
        """
        Start the flow extra fast!
        """
        if not self.is_flowing:
            self.step_time = 300
            self.score_board.score += self.level.time_left * 10
            self.score_board.score += 500
            self.level.time_left = 0
            pygame.event.post(pygame.event.Event(CUSTOM_EVENT.ADVANCE_TIMER))
        else:
            pygame.time.set_timer(CUSTOM_EVENT.STEP_FLOW, 300)
            
    
    def exit(self):
        """
        Credits + your score...
        """
        #print self.wins
        sur = pygame.image.load(data.filepath(self.main_options["exit_screen"])).convert()
        score = self.score_board.time_font.render(str(self.score_board.score), True, COLORS["red"])
        wins = self.score_board.time_font.render(str(self.wins[1]), True, COLORS["red"])
        
        sur.blit(score, ini_list_to_rect(self.main_options["exit_score_rect"]))
        sur.blit(wins, ini_list_to_rect(self.main_options["exit_wins_rect"]))
        
        self.show_pic(sur)
    
    def pause(self):
        """
        Pause the game, blanking the screen.
        """
#        print "paused"
        self.paused = True
        self.screen.blit(self.pause_surface, self.screen.get_rect())
        pygame.display.flip()
    
    def help(self):
        """
        Same as pause, only show a help screen.
        """
#        print "helped"
        self.paused = True
        self.screen.blit(self.help_surface, self.screen.get_rect())
        pygame.display.flip()
    
    
class PypeContainer:
    """
    A class representing a single network pipe (TWISTED PAIR!)
    """
    HEIGHT = 50
    WIDTH = 50
    
    def __getattr__(self, attr):
        """
        Some attributes need to go to the tile...
        """
        return getattr(self.tile, attr)
    
    def __init__(self, location_rect, tile):
        self.rect = location_rect
        self.tile = tile
        self.entered = False
        
        #Fill with eandom colors :):
        #self.surface.fill(random.choice(COLORS.values()))
        
    def enter(self, direction):
        if "PlusPipe" == self.tile.name:
            self.tile.noe += 1
        
            if 2 == self.tile.noe:
                global g_twisted_bonus
                g_twisted_bonus = True
            
        if self.tile.e2e.has_key(DIRECTIONS.OPPOSITES[direction]):
            return True
        
        return False
        
    
class GridClass:
    """
    The class representing the gameboard.
    """
    
    def __init__(self, all_options, score_board, pipe_generator, level, parent):
        self.level = level
        self.whole_ini = all_options
        self.options = dict(self.whole_ini.items(INI_GAME_SECTION))
        self.pipe_generator = pipe_generator
        self.parent = parent
        
        self.is_lost = False
        self.is_won = False
        
        self.rect = ini_list_to_rect(dict(self.whole_ini.items(INI_GENERAL_SECTION))["gameboard_rect"])
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.surface.fill(COLORS["red"])
        self.surface.set_alpha(255)
        #self.surface.set_colorkey(COLORS["red"])
        
        self.score_board = score_board
        
        self.columns = self.rect.width / PypeContainer.WIDTH
        self.rows = self.rect.height / PypeContainer.HEIGHT
        print "Columns %s, Rows %s" % (self.columns, self.rows)
        
        self.tiles = []
        for i in xrange(self.rows):
            row = []
            for j in xrange(self.columns):
                x_pos = PypeContainer.WIDTH * j
                y_pos = PypeContainer.HEIGHT * i
                
                pos_rect = Rect(x_pos, y_pos, PypeContainer.WIDTH, PypeContainer.HEIGHT)
                row.append(PypeContainer(pos_rect, pipes.BasePipe()))
            self.tiles.append(row)
        
        self.choose_start()
        self.choose_stop()
        
    def is_done(self):
        """
        Return true if the game has ended.
        """
        return self.is_lost or self.is_won
    
    def choose_start(self):
        """
        Choose a random place to put the start pipe.
        """
        
        start_pipe_options = dict(self.pipe_generator.pipes_options.items("start_pipe"))
        image_name = start_pipe_options["image"]
        
        exit_direction = str(random.randint(1, 4))
        start_pipe_options["image"] = os.path.join(os.path.dirname(image_name),  exit_direction + "_" + os.path.basename(image_name))
        start_pipe = pipes.StartPipe(exit_direction, start_pipe_options)
        
        x_pos = random.randint(1, self.columns - 2)
        y_pos = random.randint(1, self.rows - 2)
        print "Start pos %s, %s" % (x_pos, y_pos)
        
        self.switch_pipe(x_pos, y_pos, start_pipe)
        self.start_pipe_loc = (x_pos, y_pos)
    
    def choose_stop(self):
        """
        Choose a random place to put the start pipe.
        """
        
        pipe_options = dict(self.level.theme.options)
        image_name = pipe_options["image"]
        
        enter_direction = str(random.randint(1, 4))
        pipe_options["image"] = os.path.join(os.path.dirname(image_name),  enter_direction + "_" + os.path.basename(image_name))
        stop_pipe = pipes.StopPipe(int(enter_direction), pipe_options)
        
        while 1:
            x_pos = random.randint(1, self.columns - 2)
            y_pos = random.randint(1, self.rows - 2)
            if self.not_near_start(x_pos, y_pos):
                break
                
        print "Stop pos %s, %s" % (x_pos, y_pos)
        
        self.switch_pipe(x_pos, y_pos, stop_pipe)
        self.stop_pipe_loc = (x_pos, y_pos)
    
    def not_near_start(self, x, y):
        """
        Is the position x,y in the grid isn't on the start place.
        """
        if (x == self.start_pipe_loc[0]):
            return False
        
        if (y == self.start_pipe_loc[1]):
            return False
        
        return True
    
    def switch_pipe(self, x, y, new_pipe):
        """
        Switch the pipe in the location (x,y) with a new pipe.
        """
        self.tiles[y][x] = PypeContainer(self.tiles[y][x].rect, new_pipe)
    
    def blit(self):
        """
        Blit the gameboard on the screen.
        """
        
        for i in xrange(self.rows):
            for j in xrange(self.columns):
                self.surface.blit(self.tiles[i][j].tile.surface, self.tiles[i][j].rect)
    
    def handle_input(self, event):
        """
        Handles a mouse input event.
        """
        grid_x = mouse_x_into_tile_x(event.pos[0])
        grid_y = mouse_y_into_tile_y(event.pos[1])
        
        if not (self.tiles[grid_y][grid_x].can_build_on):
            return
        pipe_to_add = self.pipe_generator.get_next()

        self.switch_pipe(grid_x, grid_y, pipe_to_add)
    
    def start_flow(self):
        """
        Called when the network connection starts. 
        """
        #Get the start tile:
        start_tile = self.tiles[self.start_pipe_loc[1]][self.start_pipe_loc[0]]
        
        self.next_tile_pos = self.start_pipe_loc[0], self.start_pipe_loc[1]
        self.next_tile_direction = start_tile.exit
        
        return self.step_flow()
    
    def step_flow(self):
        """
        Move one tile forward on the path.
        """
        #Calculate the next tile with the postition and the direction of the current:
        self.last_tile_pos = self.next_tile_pos
        self.next_tile_pos = self.calc_next_tile(self.next_tile_pos, self.next_tile_direction)
        
#        print "---===>", self.next_tile_pos
        #If there is no such tile you lost:
        if None == self.next_tile_pos:
            self.spill(self.last_tile_pos)
            self.is_lost = True
            self.is_flowing = False
            return STEP_RETURNS.LOST
        
        elif self.stop_pipe_loc == self.next_tile_pos:
            self.won(self.next_tile_pos)
            self.is_flowing = False
            self.clear_board()
            return STEP_RETURNS.WON
        
        self.chosen_tile = self.tiles[self.next_tile_pos[1]][self.next_tile_pos[0]]
        self.chosen_tile.can_build_on = False
        if not "PlusPipe" == self.chosen_tile.name:
            self.chosen_tile.entered = True
        elif 1 < self.chosen_tile.noe:
            self.chosen_tile.entered = True
            
        self.score_board.score += int(self.chosen_tile.score)
        #Find the exit direction using the last direction:
        self.next_tile_direction = self.chosen_tile.e2e[DIRECTIONS.OPPOSITES[self.next_tile_direction]]
        
        alphad_surface = pygame.image.load(data.filepath(self.options["pipe_filler"])).convert()
        alphad_surface.set_colorkey(COLORS["white"])
        
        self.chosen_tile.surface.blit(alphad_surface, (0,0,0,0))
        
        return STEP_RETURNS.SAFE

    
    def clear_board(self):
        """
        Search each board place and find bad pipes and just not nice pipes.
        """
        for i in xrange(self.rows):
            for j in xrange(self.columns):
                cur_tile = self.tiles[i][j]
                if (not "BasePipe" == cur_tile.name) and (not cur_tile.entered):
                    self.score_board.score -= cur_tile.score
                    #print i, j, cur_tile.tile
    
    def calc_next_tile(self, (x, y), direction):
        """
        Find the next tile the network is going to. Return None for a spill.
        """
        
        #print ">>>", x, y, direction,
        
        if 1 == direction:
            next_tile_pos = (x - 1, y)
        elif 2 == direction:
            next_tile_pos = (x, y - 1)
        elif 3 == direction:
            next_tile_pos = (x + 1, y)
        elif 4 == direction:
            next_tile_pos = (x, y + 1)
        else:
            raise ValueError("Direction given (%s) is wrong!" % direction)
        
        #print next_tile_pos
        if (self.columns <= next_tile_pos[0]) or (0 > next_tile_pos[0]) or (self.rows <= next_tile_pos[1]) or (0 > next_tile_pos[1]):
            print "bad place"
            return None
        
        next_tile = self.tiles[next_tile_pos[1]][next_tile_pos[0]]
        
        if (not next_tile.is_enterable) or (next_tile.entered):
            print "not enerable, or already_filles"
            return None
        
        if not next_tile.enter(direction):
            print "rejected by next_tile.enter"
            return None
        
        return next_tile_pos
        
    def spill(self, last_tile_pos):
        """
        Symbolizes a break in the chain where a spill occurs and
        """
        self.parent.message = messages.Message("No route!", "-1000", dict(self.whole_ini.items(INI_MESSAGE_SECTION)))
        pygame.time.set_timer(CUSTOM_EVENT.MESSAGE_END, MESSAGE_TIME * 2)
        self.score_board.score -= self.level.theme.score
    
    def won(self, last_tile_pos):
        """
        ends the level!
        """
        self.parent.message = messages.Message("Server found!", str(self.level.theme.score), dict(self.whole_ini.items(INI_MESSAGE_SECTION)))
        pygame.time.set_timer(CUSTOM_EVENT.MESSAGE_END, MESSAGE_TIME * 2)
        self.score_board.score += self.level.theme.score
        

class Menu:
    """
    A menu...Finally exit, pause and FF...
    maybe difficulty.
    """
    
    def __init__(self, rect, options):
        self.rect = rect
        self.options = options
        
        self.surface = pygame.Surface((rect.width, rect.height))
        self.surface.set_colorkey(COLORS["black"])
        
        self.help_rect = ini_list_to_rect(self.options["help_rect"])
        self.help_surface, rect = data.load_image(data.filepath(self.options["help_image"]))
        self.surface.blit(self.help_surface, self.help_rect)
        
        self.pause_rect = ini_list_to_rect(self.options["pause_rect"])
        self.pause_surface, rect = data.load_image(data.filepath(self.options["pause_image"]))
        self.surface.blit(self.pause_surface, self.pause_rect)
        
        self.exit_rect = ini_list_to_rect(self.options["exit_rect"])
        self.exit_surface, rect = data.load_image(data.filepath(self.options["exit_image"]))
        self.surface.blit(self.exit_surface, self.exit_rect)
        
        self.ff_rect = ini_list_to_rect(self.options["ff_rect"])
        self.ff_surface, rect = data.load_image(data.filepath(self.options["ff_image"]))
        self.ff_surface.set_colorkey((254, 254, 254))
        self.surface.blit(self.ff_surface, self.ff_rect)
    
    def handle_input(self, (x, y)):
        """
        Handles input to the menu area.
        """
        x -= 150
        if check_point((x, y), self.exit_rect):
            return MENU_ITEMS.EXIT
        
        elif check_point((x, y), self.ff_rect):
            return MENU_ITEMS.FF
        
        elif check_point((x, y), self.help_rect):
            return MENU_ITEMS.HELP
        
        elif check_point((x, y), self.pause_rect):
            return MENU_ITEMS.PAUSE
        
        return -1
            
        
#------------------------------FUNCTIONS---------------------------------------#

def check_point((x, y), rect):
    """
    Checks if the point represented by (x,y) is in the area of the rect.
    """
    if (x > rect.left) and (x < rect.right):
        if (y < rect.bottom) and (y > rect.top):
            return True
        
    return False

def ini_list_to_rect(ini_area_string):
    """
    Tries to create a rect from the ini_area_string given.
    The string should be something like that: "x y w h".
    """
    split_measures = ini_area_string.split(" ", 4)
    split_measures = [int(i) for i in split_measures]
    
    if 4 == len(split_measures):
        return Rect(split_measures[0], split_measures[1], split_measures[2], split_measures[3])
    raise ValueError("Rect area (%s) in wrong format, stop changing ini :)" % ini_area_string)

def mouse_x_into_tile_x(x):
    """
    Turns mouse position x into tile position x.
    """
    tile_x = ((x) / PypeContainer.WIDTH) - (150 / PypeContainer.WIDTH)
    return tile_x

def mouse_y_into_tile_y(y):
    """
    Turns mouse position y into tile position y.
    """
    tile_y = ((y) / PypeContainer.HEIGHT) - (100 / PypeContainer.WIDTH)
    return tile_y

#------------------------------MAIN--------------------------------------------#

def main():
    try:
        #Remove the python CL arg, we don't need it...
        if "python" in sys.argv[0]:
            sys.argv = sys.argv[1:]
            
        #Start the game already!
        game_instance = Game(data.filepath(MAIN_INI_FILE))
        game_instance.start()
        
    except Exception, error:
        print "Program failed, here's a detailed explanation:"
        print error
        if DEBUG:
            print "Taceback stack:"
            import traceback
            print traceback.print_exc()