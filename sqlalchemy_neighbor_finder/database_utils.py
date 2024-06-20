import os
import pickle
import argparse
from pathlib import Path

from database_init import session, Embeddings


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path_to_classes',
        help='Path to persons (~/reid_dataset/classes)',
        type=Path
    )
    print(parser)
    return parser.parse_args()


def filling_db_table(path_to_dataset):
    dirs = os.listdir(path_to_dataset)
    for person_dir_name in dirs:
        cur_dir = os.path.join(path_to_dataset, person_dir_name)
        for file_name in os.listdir(cur_dir):
            if file_name.endswith('.pkl'):
                embedding = _get_embedding(os.path.join(cur_dir, file_name))
                crop_id = _get_crop_id(file_name)
                write_row_to_db(
                    embedding.tolist(), crop_id, person_dir_name
                )


def write_row_to_db(vector, crop_id, class_name):
    row = Embeddings(
        embedding_vector=vector,
        crop_id=crop_id,
        class_name=class_name
    )
    session.add(row)
    session.commit()


def _get_embedding(path_to_pkl):
    with open(path_to_pkl, 'rb') as fp:
        data = pickle.load(fp)
        embedding = data.get('embedding')
        return embedding


def _get_crop_id(file_name):
    expansion_shear = 4
    return file_name[:-expansion_shear]


if __name__ == "__main__":
    args = parse_args()
    filling_db_table(args.path_to_classes)
