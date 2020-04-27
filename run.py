import pandas as pd
import urllib.request
import os
from skimage.color import rgb2hsv
from skimage.color import rgb2gray
from skimage import io
import numpy as np
import random

import sys
sys.path.insert(0, f"{sys.path[0]}/src")
from etl import *

def main():
    cfg = json.load(open('config/params.json'))

    books_5_genres = pd.read_csv('notebooks/2500_books_5_genres.csv')
    genre_list = ['Fantasy', 'Romance', 'Crime', 'Horror', 'Science']

    metadata = sample_genres(genre_list,
     cfg['sample_size'], books_5_genres,
      cfg['image_folder'], cfg['meta_folder'])

if __name__ == '__main__':
    if 'test' in arguments:
        main()
