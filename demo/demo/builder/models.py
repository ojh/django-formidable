from django.db import models


class People(models.Model):

    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.CharField(max_length=256)
    salary = models.CharField(max_length=256)
    birth_date = models.DateField(max_length=256)
    grade = models.CharField(choices=[
        ('jedi', 'jedi'),
        ('padawan', 'padawan'),
        ('master', 'master')
    ], max_length=128)
