# Generated by Django 3.1 on 2020-09-10 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_categories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categories',
            name='products',
        ),
        migrations.RemoveField(
            model_name='categories',
            name='value',
        ),
        migrations.AddField(
            model_name='categories',
            name='name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(to='main.Categories'),
        ),
    ]
