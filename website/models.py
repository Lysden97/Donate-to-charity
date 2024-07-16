from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'


class Institution(models.Model):
    CHOICES = (
        (1, 'fundacja'),
        (2, 'organizacja pozarządowa'),
        (3, 'zbiórka lokalna'),
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.IntegerField(choices=CHOICES, default=1)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return f'{self.name}'


class Donation(models.Model):
    quantity = models.IntegerField()
    categories = models.ManyToManyField(Category)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, default=1)
    address = models.CharField(max_length=255, blank=True, default='')
    phone_number = models.CharField(max_length=20, blank=True, default='')
    city = models.CharField(max_length=255, blank=True, default='')
    zip_code = models.CharField(max_length=10, blank=True, default='')
    pick_up_date = models.DateField(blank=True, null=True)
    pick_up_time = models.TimeField(blank=True, null=True)
    pick_up_comment = models.TextField(blank=True, default='')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)



