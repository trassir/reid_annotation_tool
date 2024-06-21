import os
import pickle
import requests

from models import Person, Crop
from django.conf import settings


base_url = "http://127.0.0.1:8000/api"
persons_url = f"{base_url}/persons/"
crops_url = f"{base_url}/crops/"


def create_person(person):
    response = requests.post(persons_url, json=person)
    if response.status_code == 201:
        print(f"Создана персона: {person['id']}")
    else:
        print(f"Ошибка при создании персоны: {response.text}")


def create_crop(crop):
    response = requests.post(crops_url, json=crop)
    if response.status_code == 201:
        print(f"Создан кроп: {crop['id']}")
    else:
        print(f"Ошибка при создании кропа: {response.text}")


def _get_embedding(path_to_pkl):
    with open(path_to_pkl, 'rb') as fp:
        data = pickle.load(fp)
        embedding = data.get('embedding')
        return embedding


def _get_crop_id(file_name):
    expansion_shear = 4
    return file_name[:-expansion_shear]


def filling_db_table(path_to_dataset):
    dirs = os.listdir(path_to_dataset)
    for person_dir_name in dirs:
        cur_dir = os.path.join(path_to_dataset, person_dir_name)

        item = Person(
            id=person_dir_name, crop_ids=[
                _get_crop_id(crop_id) for crop_id in os.listdir(cur_dir)
            ]
        )
        item.save()
        # Adding a person via API TODO just in case
        # create_person(
        #     {
        #         "id": person_dir_name,
        #         "crop_ids": [
        #             _get_crop_id(crop_id) for crop_id in os.listdir(cur_dir)
        #         ]
        #     }
        # )

        for file_name in os.listdir(cur_dir):
            if file_name.endswith('.pkl'):
                embedding = _get_embedding(os.path.join(cur_dir, file_name))
                crop_id = _get_crop_id(file_name)

                # Adding a person via API TODO just in case
                # create_crop({"id": crop_id, "embedding": embedding.tolist()})
                item = Crop(
                    id=crop_id, embedding=embedding.tolist()
                )
                item.save()


filling_db_table(settings.MEDIA_ROOT)
