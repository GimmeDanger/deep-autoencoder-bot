# TODO: finalize description

import os
import pandas as pd
import numpy as np
from skimage.io import imread
from skimage.transform import resize
from tqdm import tqdm

dataset_path = "lfw_dataset"
images_name = "lfw-deepfunneled"
attrs_name = "lfw_attributes.txt"


def get_lfw_dataset():
    if not os.path.exists(dataset_path):
        os.mkdir(dataset_path)

    os.chdir(dataset_path)

    if not os.path.exists(images_name):
        print("images not found, downloading...")
        os.system(f"wget http://vis-www.cs.umass.edu/lfw/{images_name}.tgz -O tmp.tgz")
        print("extracting...")
        os.system("tar xvzf tmp.tgz && rm tmp.tgz")
        assert os.path.exists(images_name)
        print("done")

    if not os.path.exists(attrs_name):
        print("attributes not found, downloading...")
        os.system(f"wget http://www.cs.columbia.edu/CAVE/databases/pubfig/download/{attrs_name}")
        assert os.path.exists(attrs_name)
        print("done")

    os.chdir("..")


def del_vlw_dataset():
    import shutil
    if os.path.exists(dataset_path):
        print("deleting dataset...")
        shutil.rmtree(dataset_path)
        assert not os.path.exists(dataset_path)
        print("done")


def load_data(dx=80, dy=80, dimx=45, dimy=45):
    # fetch dataset
    if not os.path.exists(dataset_path):
        get_lfw_dataset()

    os.chdir(dataset_path)

    # read attrs
    df_attrs = pd.read_csv(attrs_name, sep='\t', skiprows=1)
    df_attrs = pd.DataFrame(df_attrs.iloc[:, :-1].values, columns=df_attrs.columns[1:])
    df_attrs = df_attrs.astype({"imagenum": int})

    # read photos
    photo_ids = []
    with tqdm(desc="Reading photos   ", total=len(df_attrs)) as pbar_outer:
        for dirpath, dirnames, filenames in os.walk(images_name):
            for fname in filenames:
                if fname.endswith(".jpg"):
                    fpath = os.path.join(dirpath, fname)
                    photo_id = fname[:-4].replace('_', ' ').split()
                    person_id = ' '.join(photo_id[:-1])
                    photo_number = int(photo_id[-1])
                    photo_ids.append({'person': person_id, 'imagenum': photo_number, 'photo_path': fpath})
                    pbar_outer.update(1)
    photo_ids = pd.DataFrame(photo_ids)

    # mass-merge (photos now have same order as attributes)
    df = pd.merge(df_attrs, photo_ids, on=('person', 'imagenum'))
    assert len(df) == len(df_attrs), "lost some data when merging dataframes"

    # image preprocessing
    all_photos = []
    photo_paths = df['photo_path']
    with tqdm(desc="Processing photos", total=len(photo_paths)) as pbar_outer:
        for path in photo_paths:
            img = imread(path)
            img = img[dy:-dy, dx:-dx]
            img = resize(img, [dimx, dimy], mode='reflect', anti_aliasing=True)
            all_photos.append(img.astype('uint8'))
            pbar_outer.update(1)

    all_photos = np.stack(all_photos)
    all_attrs = df.drop(["photo_path", "person", "imagenum"], axis=1)

    os.chdir("..")

    return all_photos, all_attrs

load_data()


