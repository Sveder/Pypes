'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''

import os

import pygame

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))

def filepath(filename):
    '''Determine the path to a file in the data directory.
    '''
    return os.path.join(data_dir, filename)

def load(filename, mode='rb'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    return open(os.path.join(data_dir, filename), mode)

def load_image(path):
        """
        Load the image by it's path and returns it and its rect.
        """
        try:
            #Check if the file exists:
            assert os.path.isfile(path) , "A game file doesn't exist: %s" % path
            
            #Load the image and return the needed values:
            image = pygame.image.load(path).convert()
            rect = image.get_rect()
            return image , rect
        except Exception , error:
            error = "Loading image (%s) failed:\n %s" % (path , error)
            raise