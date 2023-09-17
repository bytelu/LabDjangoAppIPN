# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Carrera(models.Model):
    carrera = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'carrera'


class Computadora(models.Model):
    numero = models.IntegerField()
    estado = models.IntegerField()
    laboratorio = models.IntegerField()
    cod_monitor = models.CharField(max_length=150, blank=True, null=True)
    cod_cpu = models.CharField(max_length=150, blank=True, null=True)
    ocupada = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'computadora'


class Encargado(models.Model):
    nombre = models.CharField(max_length=50)
    apellido_p = models.CharField(max_length=40)
    apellido_m = models.CharField(max_length=40)
    hora_entrada = models.TimeField(blank=True, null=True)
    hora_salida = models.TimeField(blank=True, null=True)
    usuario = models.CharField(unique=True, max_length=25)
    contrasenia = models.CharField(max_length=50)
    estado = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'encargado'


class Estudiante(models.Model):
    nombre = models.CharField(max_length=50)
    apellido_p = models.CharField(max_length=40)
    apellido_m = models.CharField(max_length=40)
    boleta = models.CharField(unique=True, max_length=15)
    grupo = models.CharField(max_length=10, blank=True, null=True)
    qr = models.CharField(unique=True, max_length=200, blank=True, null=True)
    carrera = models.ForeignKey(Carrera, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'estudiante'


class Profesor(models.Model):
    nombre = models.CharField(max_length=50)
    apellido_p = models.CharField(max_length=40)
    apellido_m = models.CharField(max_length=40)
    boleta = models.CharField(unique=True, max_length=15)
    qr = models.CharField(unique=True, max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profesor'


class Reporte(models.Model):
    titulo = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=200)
    hora = models.TimeField()
    fecha = models.DateField()
    seguimiento = models.CharField(max_length=200, blank=True, null=True)
    encargado = models.ForeignKey(Encargado, models.DO_NOTHING)
    computadora = models.ForeignKey(Computadora, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reporte'


class Sesion(models.Model):
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_final = models.TimeField(blank=True, null=True)
    activo = models.IntegerField() 
    encargado = models.ForeignKey(Encargado, models.DO_NOTHING)
    estudiante = models.ForeignKey(Estudiante, models.DO_NOTHING)
    profesor = models.ForeignKey(Profesor, models.DO_NOTHING, blank=True, null=True)
    computadora = models.ForeignKey(Computadora, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sesion'
