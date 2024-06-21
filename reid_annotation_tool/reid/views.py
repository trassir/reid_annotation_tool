import os
import shutil

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from pgvector.django import L2Distance
from django.db.models import Q

from django.conf import settings
from .models import Person, Crop
from .serializers import PersonSerializer, CropSerializer


def index(request):
    return render(request, 'index.html')


class PersonViewSet(viewsets.ModelViewSet):
    """
    methods:
     - list: Get a list of all persons
     - create: Create a new person
     - retrieve: Retrieve a person by ID
     - update: Update information about the person
     - partial_update: Partially update information about a person
     - destroy: Delete a person
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class CropViewSet(viewsets.ModelViewSet):
    """
    methods:
     - list: Get a list of all crops
     - create: Create a new crop
     - retrieve: Retrieve crop by ID
     - update: Update crop information
     - partial_update: Partially update crop information
     - destroy: Delete crop

    other methods:
    - move: Move the crop to another person
    - similar: Find similar crops
    """
    queryset = Crop.objects.all()
    serializer_class = CropSerializer

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """
        Move crop to another person

        :arg
        - person_id: New person id

        :return
        - Status message
        """
        new_path_to_dir = None
        crop = self.get_object()
        new_person_id = request.data.get('person_id')
        if not new_person_id:
            return Response({'error': 'person_id is required'}, status=400)
        try:
            new_person = Person.objects.get(id=new_person_id)
        except Person.DoesNotExist:
            new_path_to_dir = self.create_new_person(new_person_id)
            new_person = Person.objects.get(id=new_person_id)

        old_person = Person.objects.filter(crop_ids__contains=[crop.id])

        # TODO Think about the storage method
        pkl_file_ext = '.pkl'
        png_file_ext = '.png'

        for person in old_person:
            if person.id != new_person_id:
                person.crop_ids.remove(crop.id)

                path_to_dataset = settings.MEDIA_ROOT
                new_path_to_dir = os.path.join(path_to_dataset, new_person_id)
                path_to_pkl = os.path.join(
                    settings.MEDIA_ROOT, person.id, crop.id + pkl_file_ext
                )
                path_to_png = os.path.join(
                    settings.MEDIA_ROOT, person.id, crop.id + png_file_ext
                )

                if new_path_to_dir:
                    shutil.copy2(
                        path_to_png,
                        new_path_to_dir
                    )
                    shutil.copy2(
                        path_to_pkl,
                        new_path_to_dir
                    )
                os.remove(path_to_pkl)
                os.remove(path_to_png)
                person.save()

        new_person.crop_ids.append(crop.id)
        new_person.save()
        return Response({'status': 'crop moved'})

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """
        Find similar crops by crop ID

        :return
        - Message and list of similar crops
        """

        emb = self.get_embedding(pk)
        res = Crop.objects.order_by(L2Distance('embedding', emb))[:10].all()

        result = {}

        for c_ in res:
            persons_res = Person.objects.filter(
                Q(crop_ids__contains=[c_.id])
            ).first()
            result[c_.id] = persons_res.id

        return Response({
            "message": "Похожие кропы",
            "similar_crops": [i.id for i in res],
            "persons": result
        })

    def destroy(self, request, *args, **kwargs):
        """Removes crop and updates crop_ids lists for all persons"""
        crop = self.get_object()
        person = Person.objects.filter(crop_ids__contains=[crop.id]).first()
        person.crop_ids.remove(crop.id)
        person.save()
        return super().destroy(request, *args, **kwargs)

    @staticmethod
    def get_embedding(crop_id):
        crop = Crop.objects.get(id=crop_id)
        embedding = crop.embedding
        return embedding

    @staticmethod
    def create_new_folder(folder_name):
        path_to_dataset = settings.MEDIA_ROOT
        new_path = os.path.join(path_to_dataset, folder_name)
        os.mkdir(new_path)
        return new_path

    def create_new_person(self, person_id):
        item = Person(
            id=person_id, crop_ids=[]
        )
        item.save()
        new_path_to_folder = self.create_new_folder(person_id)
        return new_path_to_folder
