# Generated by Django 3.1.4 on 2021-03-03 21:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0009_auto_20210302_2143'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.cart', verbose_name='Cart'),
        ),
    ]