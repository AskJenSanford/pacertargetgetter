from django.urls import path
from .views import CaseNumberView

urlpatterns = [
    path('get-case-number/', CaseNumberView.as_view(), name='get-case-number'),
]
