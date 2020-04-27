import pandas as pd
import urllib.request
import os
from skimage.color import rgb2hsv
from skimage.color import rgb2gray
from skimage import io
import numpy as np
import random

def sample_genres(list_of_genres, sample_size, df, folder):
    df = df.drop(df[df.cover_id == 'None'].index)
    sampled_df = pd.DataFrame()
    for genre in genre_list:
        sampled_df = pd.concat([df[df.genre == genre].sample(int(sample_size/5)), sampled_df])
#     print(len(df))
    metadata = download_images(sampled_df, folder)
    pd.to_csv('src/metadata.csv', index = False)
    return sampled_df


# get pixel counts
def pixcount(painting):
    return painting.shape[0] * painting.shape[1]

#get saturation
def mean_saturation(link):
    hsv_img = rgb2hsv(link)
    saturation_img = hsv_img[:,:, 1]
    satur = np.mean(saturation_img, axis=(0,1))
    return satur

#get hue
def mean_hue(link):
    hsv_img = rgb2hsv(link)
    hue_img = hsv_img[:, :, 0]
    return np.mean(hue_img, axis=(0,1))

#get brightness
def mean_brightness(link):
    hsv_img = rgb2hsv(link)
    value_img = hsv_img[:, :, 2]
    return np.mean(value_img)

#creates folder of the passed in param
def create_directory (folder):

    if not os.path.isdir(folder):
        os.makedirs(folder)

#downloads images and extracts features
def download_images(meta_df, folder):
    create_directory(folder)
    pix = []
    brightness = []
    hue = []
    saturation = []
    count = 0
    for coverid in meta_df['cover_id']:
        if coverid == 'None':
            continue
        link = "http://covers.openlibrary.org/b/id/{}-L.jpg".format(coverid)

        rendered_link = io.imread(link)

        pix.append(pixcount(rendered_link))
        brightness.append(mean_brightness(rendered_link))
        hue.append(mean_hue(rendered_link))
        saturation.append(mean_saturation(rendered_link))

        filename = "{}/{}.jpg".format(folder,coverid)
        urllib.request.urlretrieve(link, filename)
    meta_df['pixel_count'] = pix
    meta_df['mean_brightness'] = brightness
    meta_df['mean_hue'] = hue
    meta_df['mean_saturation'] = saturation

    return meta_df
