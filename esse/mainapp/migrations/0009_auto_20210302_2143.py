# Generated by Django 3.1.6 on 2021-03-02 18:43

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0008_auto_20210301_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biography',
            name='image',
            field=models.ImageField(upload_to='', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='economics',
            name='image',
            field=models.ImageField(upload_to='', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='history',
            name='image',
            field=models.ImageField(upload_to='', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='medicine',
            name='image',
            field=models.ImageField(upload_to='', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='novel',
            name='image',
            field=models.ImageField(upload_to='', verbose_name='Image'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255, verbose_name='First name')),
                ('last_name', models.CharField(max_length=255, verbose_name='Last name')),
                ('phone', models.CharField(max_length=20, verbose_name='Phone number')),
                ('address', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Address')),
                ('status', models.CharField(choices=[('new', 'New order'), ('in_progress', 'Order in progress'), ('is_ready', 'Order is ready'), ('completed', 'Order is completed')], default='new', max_length=100, verbose_name='Order status')),
                ('purchase_type', models.CharField(choices=[('self', 'Self-pickup'), ('delivery', 'Delivery')], default='self', max_length=100, verbose_name='Purchase type')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment form')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Order creating date')),
                ('order_date', models.DateField(default=django.utils.timezone.now, verbose_name='Order processing date')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_orders', to='mainapp.customer', verbose_name='Customer')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='orders',
            field=models.ManyToManyField(related_name='related_customer', to='mainapp.Order', verbose_name='Customer orders'),
        ),
    ]
