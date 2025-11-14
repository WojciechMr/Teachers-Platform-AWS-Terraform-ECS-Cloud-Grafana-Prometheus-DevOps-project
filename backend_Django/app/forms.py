from django import forms
from .models import CalendarEvent

class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title', 'date', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'p-2 rounded text-gray-900', 'placeholder': 'Tytuł wydarzenia'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'p-2 rounded text-gray-900'}),
            'description': forms.TextInput(attrs={'class': 'p-2 rounded text-gray-900', 'placeholder': 'Opis (opcjonalny)'}),
        }


from django import forms
from .models import SchoolClass, ClassLesson

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'p-2 rounded text-gray-900', 'placeholder': 'Nazwa klasy'})
        }


class AddLessonToClassForm(forms.Form):
    lesson = forms.ModelChoiceField(
        queryset=None,  # ustawimy dynamicznie w widoku
        empty_label="Wybierz lekcję",
        widget=forms.Select(attrs={'class': 'p-2 rounded text-gray-900'})
    )


from django import forms
from .models import StudentClass, Student, Grade

class StudentClassForm(forms.ModelForm):
    class Meta:
        model = StudentClass
        fields = ['name', 'subject']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'notes']

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['value', 'description']
