from django.db import models
from math import radians, sin, cos, sqrt, atan2

opt_staff = [
    [0, 'Brigadista'],
    [1, 'Profesor'],
]

opt_faculty = [
    [0, 'Salud'],
    [1, 'Energía'],
    [2, 'Jurídica'],
    [3, 'Educativa'],
    [4, 'Agropecuaria'],
]

class Staff(models.Model):
    dni = models.CharField(max_length=10, unique=True)
    name =  models.CharField(max_length=30)
    last_name =  models.CharField(max_length=50)
    email = models.CharField(max_length=320, unique=True)
    phone_number = models.CharField(max_length=12, unique=True)
    staff_type = models.IntegerField(choices=opt_staff)
    faculty = models.IntegerField(choices=opt_faculty, null=True) 

    def __str__(self):
        return f"{self.name} -> {self.staff_type}"

class Node(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    is_safe = models.CharField(max_length=1, null=False)

    def __str__(self):
        return self.name
    
class Connection(models.Model):
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='source')
    destination = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='destination')
    weight = models.FloatField(null=False)

    def __str__(self):
        return f'Conex[{self.source}, {self.destination}, {self.weight}]'

    def calculate_distance(self):
        R = 6371

        lat1, lon1 = radians(self.source.latitude), radians(self.source.longitude)
        lat2, lon2 = radians(self.destination.latitude), radians(self.destination.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c * 1000

        return distance

    def save(self, *args, **kwargs):
        self.weight = self.calculate_distance()
        super().save(*args, **kwargs)

        reverse_connection_exists = Connection.objects.filter(
            source=self.destination,
            destination=self.source
        ).exists()

        if not reverse_connection_exists:
            # Crear la conexión inversa con el peso calculado
            reverse_connection = Connection(
                source=self.destination,
                destination=self.source,
                weight=self.weight
            )
            reverse_connection.save()

class Brigade(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return f'{self.name}'

class FunctionsBrigade(models.Model):
    brigade = models.ForeignKey(Brigade, on_delete=models.CASCADE)
    function = models.CharField(max_length=300, null=False)

    def __str__(self):
        return f'{self.brigade}, {self.function}'

class Map(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    img = models.ImageField(upload_to="maps", null=True)

    def __str__(self):
        return self.name
