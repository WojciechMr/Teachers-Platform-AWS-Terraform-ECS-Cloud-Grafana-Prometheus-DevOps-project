from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class LessonUsage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    used_lessons = models.IntegerField(default=0)
    max_lessons = models.IntegerField(default=1000)  # np. 10 lekcji na miesiąc
    last_reset = models.DateTimeField(default=timezone.now)

    def reset_if_needed(self):
        """Resetuje licznik raz w miesiącu"""
        now = timezone.now()
        if now.month != self.last_reset.month or now.year != self.last_reset.year:
            self.used_lessons = 0
            self.last_reset = now
            self.save()


class GeneratedLesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    duration = models.IntegerField()  # 20 lub 45
    content = models.TextField()  # wygenerowana lekcja
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']  # najnowsze najpierw
    def __str__(self):
        # Wyświetli np. "Matematyka - 45 min"
        return f"{self.topic} ({self.duration} min)"


class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey('GeneratedLesson', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz do: {self.lesson.topic}"
    

from django.db import models
from django.contrib.auth.models import User

class CalendarEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.date})"
    

from django.db import models
from django.contrib.auth.models import User
from .models import GeneratedLesson

class SchoolClass(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # właściciel klasy
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ClassLesson(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="lessons")
    lesson = models.ForeignKey(GeneratedLesson, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson.topic} -> {self.school_class.name}"
    

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title} ({self.date})"
    

class StudentClass(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='students')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    average_grade = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def average(self):
        grades = self.grades.all()
        if not grades.exists():
            return None
        total_weighted = sum([g.value * g.weight for g in grades])
        total_weight = sum([g.weight for g in grades])
        if total_weight == 0:
            return None
        return round(total_weighted / total_weight, 2)




class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    value = models.IntegerField()
    description = models.CharField(max_length=200, blank=True)
    weight = models.PositiveIntegerField(default=1)  # nowa kolumna waga
    weight_description = models.CharField(max_length=200, blank=True)  # nowa kolumna opis wagi
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.value} - {self.student}"