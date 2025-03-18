from django.db import models

class Student(models.Model):
    student_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField()

    def __str__(self):
        return self.student_number


class Room(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name


class Reservation(models.Model):
    # Définissez un étudiant par défaut (en supposant qu'il existe un étudiant avec l'ID 1)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, default=1)
    # Définissez une salle par défaut (en supposant qu'une salle avec l'ID 1 existe)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, default=1)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    motif = models.TextField(default="Motif par défaut")
    participants = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Reservation by {self.student} in {self.room} on {self.date}"

