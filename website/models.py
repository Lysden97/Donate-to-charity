from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Institution(models.Model):
    FOUNDATION = 'fundacja'
    NGO = 'organizacja pozarządowa'
    LOCAL_COLLECTION = 'zbiórka lokalna'

    CHOICES = (
        (FOUNDATION, 'fundacja'),
        (NGO, 'organizacja pozarządowa'),
        (LOCAL_COLLECTION, 'zbiórka lokalna'),
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=100, choices=CHOICES, default=FOUNDATION)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return f'{self.name} - {self.get_type_display()}'

    class Meta:
        verbose_name = 'Instytucja'
        verbose_name_plural = 'Instytucje'


class Donation(models.Model):
    quantity = models.IntegerField()
    categories = models.ManyToManyField(Category)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    pick_up_date = models.DateField(null=True)
    pick_up_time = models.TimeField(null=True)
    pick_up_comment = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_taken = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.quantity} bags for {self.institution.name}'
