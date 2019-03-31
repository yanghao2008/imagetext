from django.db import models

# Create your models here.

class BooksImageText(models.Model):
    book = models.ForeignKey('Info', to_field='book_id', on_delete=models.CASCADE)
    text = models.TextField()
    page = models.TextField()
    chapter = models.TextField()
    image = models.TextField()
    txt = models.TextField()

class Info(models.Model):
    book_id = models.TextField(unique=True)
    author = models.TextField()
    bookname = models.TextField()
    pubaddress = models.TextField()
    publisher = models.TextField()
    year = models.TextField()
