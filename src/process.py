import umap.umap_ as umap
from PIL import Image
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import seaborn as sns
from matplotlib import pyplot as plt
# import pytesseract
# from pytesseract import Output
%matplotlib inline

### RGB HISTOGRAM ###

def get_rgb_hist(metadata,img_path):
    lst_rgb_hist = []
    for cover_id in metadata['cover_id']:
        path = img_path+"/"+str(cover_id)+".jpg"
        image = cv2.imread(path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8],[0, 256, 0, 256, 0, 256])
        norm_hist = cv2.normalize(hist, None)
        lst_rgb_hist.append(norm_hist)
    return lst_rgb_hist

def get_hist_corr(lst_rgb_hist):
    lst_img_corr = []
    for i in range(len(lst_rgb_hist)):
        i_hist = lst_rgb_hist[i]
        lst_corr = []
        for j in range(len(lst_rgb_hist)):
            j_hist = lst_rgb_hist[j]
            corr = cv2.compareHist(i_hist, j_hist, cv2.HISTCMP_CORREL)
            lst_corr.append(corr)
        lst_img_corr.append(lst_corr)
    return lst_img_corr


def get_max_corr(lst_img_corr):
    lst_max_corr_idx = []
    for i in range(len(lst_img_corr)):
        lst_corr = lst_img_corr[i]
        max_corr = 0
        max_corr_idx = 0
        for j in range(len(lst_corr)):
            corr = lst_corr[j]
            if corr == 1:
                continue
            else:
                if corr > max_corr:
                    max_corr = corr
                    max_corr_idx = j
        lst_max_corr_idx.append(max_corr_idx)
    return lst_max_corr_idx

def add_sim_book_col(metadata,lst_max_corr_idx):
    lst_max_corr_cover_id = []
    for idx in lst_max_corr_idx:
        row = metadata.iloc[idx]
        lst_max_corr_cover_id.append(row['cover_id'])
    metadata['Most Similar Book'] = pd.Series(lst_max_corr_cover_id)
    return metadata

def create_umap_rgb_hist(lst_rgb_hist,metadata):
    lst_rgb_hist_flat = []
    for hist in lst_rgb_hist:
        lst_rgb_hist_flat.append(hist.flatten())
    reducer = umap.UMAP()
    embedding = reducer.fit_transform(lst_rgb_hist_flat)
    umap_df = pd.DataFrame(embedding, columns=('x', 'y'))
    umap_df['label'] = metadata['genre']
    plt.figure(figsize=(15,16))
    rgb_hist_umap = sns.lmplot( x="x", y="y", data=umap_df, fit_reg=False, hue='label', legend=True)
    rgb_hist_umap.savefig("rgb_hist_umap.png")
    return umap_df

def create_img_thumbnails(metadata,image_path,thumbnail_path):
    size = 24, 32
    lst_thumbnails = []
    lst_thumbnail_path = []
    for cover_id in metadata['cover_id']:
        path = image_path+"/"+str(cover_id)+".jpg"
        im = Image.open(path)
        im.thumbnail(size)
        thumbnail_path = thumbnail_path+'/'+str(cover_id)+'.jpg'
        im.save(thumbnail_path)
        lst_thumbnail_path.append(thumbnail_path)
        lst_thumbnails.append(thumbnail_path)
    return lst_thumbnails

def create_umap_rgb_hist_with_tn(umap_df):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.scatter(umap_df['x'].values, umap_df['y'].values) 
    coords = umap_df[['x','y','thumnail_path']].values
    for i in range(len(coords)):
        img = OffsetImage(plt.imread(coords[i][2]))
        ab = AnnotationBbox(img, (coords[i][0], coords[i][1]), frameon=False)
        ax.add_artist(ab)

    plt.title('UMAP of Book Covers')
    fig.savefig('output/UMAP of Book Covers.jpg')


### ORB ###


def get_keypoints_and_desc(metadata,image_path):
    orb = cv2.ORB_create()
    lst_kd = []
    lst_desc = []
    cnt_none = 0
    for cover_id in metadata['cover_id']:
        path = image_path+"/"+str(cover_id)+".jpg"
        image = cv2.imread(path)
        try:
            gray = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
            keypoint, descriptor = orb.detectAndCompute(gray, None)
            lst_kd.append([keypoint,descriptor])
            lst_desc.append(descriptor)
        except Exception as e:
            print(e)
            cnt_none += 1
            lst_kd.append([[],None])
            lst_desc.append(None)
    return lst_desc,lst_kd

def get_best_matches(lst_desc,lst_kd):
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)
    lst_best_match = []
    for i in range(len(lst_kd)):
        if i % 100 == 0:
            print(i," Covers Done")
        i_kd = lst_kd[i]
        if i_kd[1] is None:
            lst_best_match.append(None)
            continue
        min_dist = 99999999
        min_dist_idx = None
        for j in range(len(lst_kd)):
            j_kd = lst_kd[j]
            if j_kd[1] is None:
                continue
            matches = bf.match(i_kd[1], j_kd[1])
            good = sorted(matches, key = lambda x : x.distance)[:10]
            total_distance = 0
            for m in good:
                total_distance += m.distance
            avg_dist = total_distance / len(good)
            if 0 < avg_dist < min_dist:
                min_dist = avg_dist
                min_dist_idx = j
        lst_best_match.append(min_dist_idx)
    return lst_best_match

def add_best_match_col(metadata,lst_best_match):
    lst_best_match_cover_id = []
    for idx in lst_best_match:
        if idx is None:
            lst_best_match_cover_id.append(None)
            continue
        match_cover_id = metadata['cover_id'].iloc[idx]
        lst_best_match_cover_id.append(str(match_cover_id))
    metadata['Best Match'] = pd.Series(lst_best_match_cover_id)
    return metadata

def create_orb_acc_hist(metadata):
    correct = 0
    lst_correctly_matched = []
    for cover in metadata['cover_id'].tolist():
        cover_metadata = metadata[metadata['cover_id']==cover]
        cover_genre = cover_metadata['genre'].iloc[0]
        bm = cover_metadata['Best Match'].iloc[0]
        if bm is None or pd.isnull(bm):
            continue
        bm_genre = metadata[metadata['cover_id']==int(bm)]['genre'].iloc[0]
        if cover_genre == bm_genre:
            correct += 1
            lst_correctly_matched.append(1)
        else:
            lst_correctly_matched.append(0)
    metadata['Correct_Match'] = pd.Series(lst_correctly_matched)
    metadata[metadata['Correct_Match']==0]['genre'].hist(figsize=(15,10))
    ax.figure.savefig('orb_acc_hist.png')

