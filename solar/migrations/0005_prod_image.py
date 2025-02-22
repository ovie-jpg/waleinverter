# Generated by Django 4.2.9 on 2024-06-29 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('solar', '0004_alter_blog_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prod_image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='media')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='solar.product')),
            ],
        ),
    ]
