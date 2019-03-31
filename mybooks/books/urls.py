from django.urls import path
from . import books_views

urlpatterns = [
    path('books/', books_views.index, name='books'),
]

