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
    category = models.ManyToManyField(Category)

    def __str__(self):
        return f'{self.name}'
