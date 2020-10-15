# Generated by Django 3.1 on 2020-09-10 08:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20200905_1446'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('products', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Categories', to='main.product')),
            ],
        ),
    ]
