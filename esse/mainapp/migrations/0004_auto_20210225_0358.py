# Generated by Django 3.1.4 on 2021-02-25 00:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_auto_20210225_0350'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='products',
        ),
        migrations.RemoveField(
            model_name='cartproduct',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='cartproduct',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='cartproduct',
            name='user',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='user',
        ),
        migrations.RemoveField(
            model_name='economics',
            name='category',
        ),
        migrations.RemoveField(
            model_name='history',
            name='category',
        ),
        migrations.RemoveField(
            model_name='medicine',
            name='category',
        ),
        migrations.RemoveField(
            model_name='novel',
            name='category',
        ),
        migrations.DeleteModel(
            name='Biography',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartProduct',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Customer',
        ),
        migrations.DeleteModel(
            name='Economics',
        ),
        migrations.DeleteModel(
            name='History',
        ),
        migrations.DeleteModel(
            name='Medicine',
        ),
        migrations.DeleteModel(
            name='Novel',
        ),
    ]