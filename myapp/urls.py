from django.urls import path
from .views import hello, name_form

urlpatterns = [
    path('api/hello', hello),
    path('', name_form, name='name_form'),
]
