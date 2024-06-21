from rest_framework.routers import DefaultRouter
from reid.views import PersonViewSet, CropViewSet


router = DefaultRouter()
router.register(r'persons', PersonViewSet)
router.register(r'crops', CropViewSet)
