import os
import shutil
import pickle
import argparse
import numpy as np
from pathlib import Path
from sklearn.neighbors import NearestNeighbors


RESULT_DIR_NAME = 'nearest_neighbors'
MAIN_LIST = []  # TODO


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='Target embedding (.pkl)', type=Path)
    parser.add_argument('output_dir', help='Output dir name', type=Path)
    parser.add_argument('--neighbors_count', default=10, help='Count for NearestNeighbors method')
    parser.add_argument('--update_model', default=False, help='Create new NearestNeighbors model')
    return parser.parse_args()


def get_crop_embeddings(vectors):
    return np.array(vectors)


def update_emb_file(crop_embeddings):
    nn = NearestNeighbors(
        n_neighbors=args.neighbors_count, metric='cosine'
    )
    nn.fit(crop_embeddings)
    MAIN_LIST.extend(crop_embeddings)
    with open('nearest_neighbors_model.pkl', 'wb') as f:
        pickle.dump(nn, f)


def get_nn(update_model):
    path_to_file = 'nearest_neighbors_model.pkl'
    if update_model:
        os.remove(path_to_file)

    if not os.path.exists(path_to_file):
        update_emb_file(get_crop_embeddings(all_emb))
    with open('nearest_neighbors_model.pkl', 'rb') as f:
        nn = pickle.load(f)
        return nn


def recreate_dir(dir_name):
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        shutil.rmtree(dir_name)
        os.mkdir(dir_name)


def replace_path_to_pkl(file_path):
    head, file_name = os.path.split(file_path)
    new_head = head.replace('ann', 'img')
    new_file_name = file_name[:-4]
    return new_head, new_file_name


def get_kneighbors_paths(update_model):
    res = []
    nn = get_nn(update_model)
    distances, indices = nn.kneighbors(target_embedding)

    recreate_dir(RESULT_DIR_NAME)

    for emb_index, emb in enumerate(get_crop_embeddings(all_emb)):
        if emb_index in indices[0]:
            file_path = pkl_manager.MAIN_DICT[tuple(emb)]
            res.append(file_path)
            new_head, new_file_name = replace_path_to_pkl(file_path)
            shutil.copy2(
                os.path.join(new_head, new_file_name), RESULT_DIR_NAME
            )
    print(res)
    return res


class PklManager:
    MAIN_DICT = {}

    def __init__(self, output_dir):
        self.__output_dir = output_dir

    @property
    def output_dir(self):
        return self.output_dir

    @output_dir.setter
    def output_dir(self, value):
        self.__output_dir = value

    def get_all_emb(self):
        return self._dataset_list_gen()

    @classmethod
    def convert_pkl_to_emb_obj(cls, path_to_pkl):
        with open(path_to_pkl, 'rb') as f:
            try:
                data = pickle.load(f)
                res_vector = data.get('embedding')
                cls.MAIN_DICT[tuple(res_vector)] = path_to_pkl
                return res_vector
            except Exception as err:
                print(err)

    @staticmethod
    def get_target_embedding(path_to_pkl):
        changed_vector = pkl_manager.convert_pkl_to_emb_obj(path_to_pkl)
        return np.array(changed_vector).reshape(1, -1)

    def _dataset_list_gen(self):
        res = []
        for index_, path_ in enumerate(os.listdir(self.output_dir)):
            cur_vector = self.convert_pkl_to_emb_obj(
                os.path.join(self.output_dir, path_)
            )
            if cur_vector.any():
                res.append(cur_vector)
        return res


if __name__ == "__main__":
    args = parse_arg()
    pkl_manager = PklManager(args.output_dir)
    all_emb = pkl_manager.get_all_emb()
    target_embedding = pkl_manager.get_target_embedding(args.target)
    get_kneighbors_paths(args.update_model)
