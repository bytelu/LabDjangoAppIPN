# Generated by Django 3.2.19 on 2023-09-08 20:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Computacion', '0007_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Carrera',
        ),
        migrations.DeleteModel(
            name='Computadora',
        ),
        migrations.DeleteModel(
            name='Encargado',
        ),
        migrations.DeleteModel(
            name='Estudiante',
        ),
        migrations.DeleteModel(
            name='Profesor',
        ),
        migrations.DeleteModel(
            name='Reporte',
        ),
        migrations.DeleteModel(
            name='Sesion',
        ),
    ]
