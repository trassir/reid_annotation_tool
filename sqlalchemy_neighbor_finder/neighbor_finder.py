import os
import shutil
import pickle
import argparse
from pathlib import Path

from sqlalchemy import select
from database_init import session, Embeddings


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('crop', help='Path to crop .pkl file', type=Path)
    parser.add_argument('limit', help='Number of nearest neighbors', type=int)
    parser.add_argument(
        '--algorithm',
        help='Search algorithm (l2_distance(default), cosine_distance, max_inner_product)',
        type=str,
        default='l2_distance'
    )
    return parser.parse_args()


def get_neighbors(path_to_crop, limit, method):
    embedding_query = _convert_pkl_to_emb_obj(path_to_crop)
    methods = {
        'l2_distance': Embeddings.embedding_vector.l2_distance,
        'cosine_distance': Embeddings.embedding_vector.cosine_distance,
        'max_inner_product': Embeddings.embedding_vector.max_inner_product,
    }
    method = methods.get(method)
    res = session.scalars(
        select(Embeddings).order_by(
            method(embedding_query.tolist())
        ).limit(limit)
    )
    return res.fetchall()


def _convert_pkl_to_emb_obj(path_to_pkl):
    with open(path_to_pkl, 'rb') as f:
        data = pickle.load(f)
        res_vector = data.get('embedding')
        return res_vector


def recreate_dir(dir_name):
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        shutil.rmtree(dir_name)
        os.mkdir(dir_name)


if __name__ == "__main__":
    args = parse_args()

    recreate_dir('./../nearest_neighbors')  # TODO
    for i in get_neighbors(
        args.crop, args.limit, args.algorithm

    ):
        print(i.crop_id)
        shutil.copy2(
            os.path.join('./../out/reid_dataset/classes', i.class_name, i.crop_id + '.png'),
            './../nearest_neighbors'
        )
