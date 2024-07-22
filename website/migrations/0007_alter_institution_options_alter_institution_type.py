# Generated by Django 5.0.7 on 2024-07-22 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_alter_donation_city_alter_donation_phone_number_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='institution',
            options={'verbose_name': 'Instytucja', 'verbose_name_plural': 'Instytucje'},
        ),
        migrations.AlterField(
            model_name='institution',
            name='type',
            field=models.IntegerField(choices=[('fundacja', 'fundacja'), ('organizacja pozarządowa', 'organizacja pozarządowa'), ('zbiórka lokalna', 'zbiórka lokalna')], default='fundacja'),
        ),
    ]
