from django.urls import path, include
from .views import CaseNumberView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'addresses', CaseNumberView)

urlpatterns = [
    path('', include(router.urls))
]
