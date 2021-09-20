# Generated by Django 3.2.4 on 2021-09-16 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zalo_base', '0004_auto_20210714_0949'),
    ]

    operations = [
        migrations.AddField(
            model_name='zalouser',
            name='payment_code',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='zalouser',
            name='regist_payment_phone',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='zalouser',
            name='phone',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='zalouser',
            name='user_id',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
