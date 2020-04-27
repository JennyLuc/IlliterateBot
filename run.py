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
from data import *

def main(targets):
    cfg = json.load(open('config/params.json'))
    limit_per_genre = cfg['limit_per_genre']
    genres = cfg['genres']
    if 'test' in targets:
            books_5_genres = pd.read_csv('notebooks/2500_books_5_genres.csv')
            metadata = sample_genres(genres,cfg['sample_size'],books_5_genres,cfg['image_folder'],cfg['meta_folder'])
            return
    if 'data' in targets:
        lst_jsons = get_genre_jsons(genres,limit_per_genre)
        df_metadata = get_metadata(genres,lst_jsons)
        write_df_to_csv(df_metadata)

    if 'eda' in targets:
        books_5_genres = pd.read_csv('notebooks/metadata.csv')
        metadata = sample_genres(genres,cfg['sample_size'],books_5_genres,cfg['image_folder'],cfg['meta_folder'])

if __name__ == '__main__':
    targets = sys.argv[1]
    main(targets)
