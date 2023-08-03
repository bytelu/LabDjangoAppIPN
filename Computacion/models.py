from django.db import models
from datetime import timedelta
from django.forms import Select

# Create your models here.

class Carrera(models.Model):
    #llave primaria por defecto
    carrera = models.CharField(max_length=50, null=False, unique=True, verbose_name='Programa Academico')
    
    def __str__(self):
        return self.carrera
    
    class Meta:
        db_table = 'career'
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'
        ordering = ['id']
    
class Computadora(models.Model):
    #llave primaria por defecto
    numero = models.IntegerField(null=False, verbose_name='Numero de Computadora')
    estado = models.BooleanField(default=True, verbose_name='Estado de computadora')
    laboratorio = models.IntegerField(null=False, verbose_name='Laboratorio')
    ##AGREGUE ESTOS DOS DE ABAJO
    cod_monitor = models.CharField(max_length=100, null=True, verbose_name='Codigo Monitor')
    cod_cpu = models.CharField(max_length=100, null=True, verbose_name='Codigo CPU')
    
    def __str__(self):
        return self.numero #laboratorio | numero de computadora
    
    class Meta:
        db_table = 'computer'
        verbose_name = 'Computadora'
        verbose_name_plural = 'Computadoras'
        ordering = ['numero'] #por laboratorio y por numero de computadoras
    
class Encargado(models.Model):
    #llave primaria por defecto
    nombre = models.CharField(max_length=100, null=False,verbose_name='Nombre')
    apellido_p = models.CharField(max_length=100, null=False,verbose_name='Apellido Paterno')
    apellido_m = models.CharField(max_length=100, null=False,verbose_name='Apellido Materno')
    hora_entrada = models.TimeField(null=True, blank=True, verbose_name='Hora de Entrada')
    hora_salida = models.TimeField(null=True, blank=True, verbose_name='Hora de Salida')
    usuario = models.CharField(max_length=50, null=False, unique=True, verbose_name='Usuario')
    contrasenia = models.CharField(max_length=128, null=False, verbose_name='Contraseña')
    estado = models.BooleanField(default=True, verbose_name='Estado')
    
    def __str__(self):
        return f"Encargado: {self.nombre} {self.apellido_p} {self.apellido_m}"
    
    class Meta:
        db_table = 'manager'
        verbose_name = 'Encargado'
        verbose_name_plural = 'Encargados'
        ordering = ['id']
    
class Reportes (models.Model):
    #Llave primaria por defecto
    titulo = models.CharField(max_length=80, null=False, unique=False, verbose_name='Titulo')
    descripcion = models.TextField(max_length=2000, null=False,unique=False,verbose_name='Descripcion')
    hora = models.TimeField(auto_now_add=True, verbose_name='Hora del Reporte')
    fecha = models.DateField(auto_now_add=True, verbose_name='Fecha del Reporte')
    seguimiento = models.TextField(max_length=2000, null=True, blank=True,unique=False,verbose_name='Seguimiento')
    #llave foranea 1 encargado tiene muchos reportes
    encargado = models.ForeignKey(Encargado, on_delete=models.CASCADE, null=False, blank=False, verbose_name='Encargado')
    #AGREGUE ESTE POR SI LAS DUDDAS
    computadora = models.ForeignKey(Computadora, verbose_name=("Computadora"), on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Reporte: {self.id}, Titulo: {self.titulo}"
    
    class Meta:
        db_table = 'report'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['fecha', 'id']
    
class Profesor (models.Model):
    #llave primaria por defecto
    nombre = models.CharField(max_length=100, null=False, verbose_name='Nombre')
    apellido_p = models.CharField(max_length=100, null=False,verbose_name='Apellido Paterno')
    apellido_m = models.CharField(max_length=100,null=False, verbose_name='Apellido Materno')
    boleta = models.IntegerField(null=False, unique=True, verbose_name='Boleta')
    #AGREGUE QR
    qr = models.CharField(max_length=200, null=True, blank=True, unique=True, verbose_name='QR')
    
    def __str__(self):
        return f"Profesor: {self.nombre} {self.apellido_p} {self.apellido_m}"
    
    class Meta:
        db_table = 'teacher'
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
        ordering = ['id', 'nombre']
    
class Alumno(models.Model):
    #llave primaria por defecto
    nombre = models.CharField(max_length=100, null=False,verbose_name='Nombre')
    apellido_p = models.CharField(max_length=100, null=False,verbose_name='Apellido Paterno')
    apellido_m = models.CharField(max_length=100, null=False,verbose_name='Apellido Materno')
    boleta = models.IntegerField(null=False, unique=True, verbose_name='Boleta')
    semestre = models.IntegerField(null=False, verbose_name='Semestre')
    #AGRGUE QR
    qr = models.CharField(max_length=200, null=True, blank=True, unique=True, verbose_name='QR')
    #llave foranea, 1 carrera tiene muchos alumnos
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, null=False, blank=False, verbose_name='Carrera')
    
    def __str__(self):
        return f"Alumno: {self.nombre} {self.apellido_p} {self.apellido_m}, Semestre: {self.semestre}"
    
    class Meta:
        db_table = 'student'
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = ['semestre','nombre']

class Sesion(models.Model):
    # Llave primaria por defecto
    fecha = models.DateField(auto_now_add=True, verbose_name='Fecha de Sesión')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_final = models.TimeField(verbose_name='Hora final')
    #Llave foranea, 1 encagado tiene muchas sesiones
    encargado = models.ForeignKey(Encargado, verbose_name=("Encargado"), on_delete=models.CASCADE)
    #Llave foranea, 1 alumno tiene muchas sesiones
    alumno = models.ForeignKey(Alumno, verbose_name=("Alumno"), on_delete=models.CASCADE)
    #Llave forane, 1 profesor tiene muchas sesiones
    profesor = models.ForeignKey(Profesor, verbose_name=("Profesor"), on_delete=models.CASCADE, null=True, blank=True)
    #Llave forane, 1 computadora tiene muchas sesiones
    computadora = models.ForeignKey(Computadora, verbose_name=("Computadora"), on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Sesion No: {self.id}, Fecha: {self.fecha}"
    
    class Meta:
        db_table = 'session'
        verbose_name = 'Sesion'
        verbose_name_plural = 'Sesiones'
        ordering = ['id','fecha']
    