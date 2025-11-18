from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import GeneratedLesson, LessonUsage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import openai
import os
from dotenv import load_dotenv
import io
from .models import GeneratedLesson, Quiz
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from .models import SchoolClass, ClassLesson, GeneratedLesson
from .forms import SchoolClassForm, AddLessonToClassForm
from django.contrib import messages
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CalendarEvent
from .forms import CalendarEventForm
from datetime import date
import calendar
from django.shortcuts import render
from .models import CalendarEvent 
from .models import StudentClass, Student, Grade 
from .forms import StudentClassForm
from .forms import StudentForm, GradeForm
import docx2txt
import PyPDF2
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from weasyprint import HTML
# ---------------------
# REJESTRACJA FONTU PDF UTF-8
# ---------------------
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))

# ---------------------
# ŁADOWANIE KLUCZA OPENAI
# ---------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------------------
# FUNKCJA POMOCNICZA
# ---------------------
def safe_str(text):
    if text is None:
        return ""
    return str(text)

# ---------------------
# AUTH
# ---------------------
@csrf_exempt
def health(request):
    return HttpResponse("OK", status=200)


def natural_sort_key(s):
    """Sortowanie naturalne, numeryczne np. screen1.png, screen2.png, screen10.png"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


import boto3
from django.conf import settings
from django.shortcuts import render

def home(request):
    # Utwórz klienta S3
    s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    prefix = 'static/images/screens/'

    # Pobierz listę obiektów w bucket
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    images = []

    for obj in response.get('Contents', []):
        key = obj['Key']
        if key.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Generuj pełny URL do S3
            images.append(f"https://{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{key}")

    # Sortowanie alfabetyczne / numeryczne
    images.sort()

    return render(request, 'home.html', {'images': images})



# ---------------------
# FUNKCJA DO FORMATOWANIA LEKCJI
# ---------------------
def clean_markdown_lesson(text):
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith("### "):
            cleaned_lines.append(f"<strong>{line[4:]}</strong>")
        elif line.startswith("#### "):
            cleaned_lines.append(f"<strong>{line[5:]}</strong>")
        elif line.startswith("- "):
            cleaned_lines.append(f"• {line[2:]}")
        elif len(line) > 2 and line[0].isdigit() and line[1] == ".":
            cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
    return "<br>".join(cleaned_lines)

from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Hasła się nie zgadzają!")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Użytkownik już istnieje!")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Wysyłka maila powitalnego
        subject = "Witamy w Edublinkier – Twoja przygoda z nauką zaczyna się teraz!"
        from_email = settings.EMAIL_HOST_USER
        to = [user.email]

        # Renderowanie HTML-owego maila
        html_content = render_to_string("welcome_email.html", {"username": user.username})
        text_content = f"Cześć {user.username}! Witamy w Edublinkier!"

        try:
            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            print("Błąd wysyłki maila:", e)

        messages.success(request, "Konto utworzone! Możesz się zalogować.")
        return redirect("login")

    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Nieprawidłowy login lub hasło!")
            return redirect("login")

    return render(request, "login.html")

@login_required(login_url="/login/")
def logout_view(request):
    logout(request)
    return redirect("home")

@login_required(login_url="/login/")
def dashboard_view(request):
    return render(request, "dashboard.html")

# ---------------------
# GENEROWANIE LEKCJI
# ---------------------
def generate_lesson_with_openai(topic, duration):
    prompt = f"""
Jesteś nauczycielem i tworzysz lekcji dla uczniów żeby dobrze ją przeprowadzić.
Temat lekcji: {topic}
Czas trwania: {duration} minut (20 lub 45)
Podziel plan na sekcje: 
1. Wprowadzenie – opowiedz o temacie, najważniejsze zagadnienia związane z tematem, omówienie oraz szczegółowa analiza,
2. Szczegóły – Podaj Szczegółowy opis tego co wygenerowałeś wszystko obszernie najlepiej tak jakbys mial poprowadzic lekcje jako nauczyciel, 
3. Ćwiczenia – Przykłady, rozwiązania, opis i rozszerzenie wygenerowanych wyżej punktów,
4. Zakończenie – podsumowanie, refleksja, naistotniejsze i najwazniejsze tematy związane z wygeneorwanym wyżej tekstem
Na końcu ewentualna praca domowa 
Formatuj w formie punktów.
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        lesson_text = str(response.choices[0].message.content)
    except Exception as e:
        lesson_text = "Błąd OpenAI: " + str(e).encode('utf-8', 'replace').decode('utf-8')
    return lesson_text

@login_required(login_url='/login/')
def generate_lesson_view(request):
    # Pobranie lub utworzenie obiektu użycia lekcji
    usage, _ = LessonUsage.objects.get_or_create(user=request.user)
    usage.reset_if_needed()
    usage.max_lessons = 100
    usage.save()

    # Sprawdzenie limitu lekcji
    if usage.used_lessons >= usage.max_lessons:
        messages.error(request, f"Osiągnąłeś limit {usage.max_lessons} lekcji w tym miesiącu!")
        return redirect('dashboard')

    if request.method == "POST":
        topic = request.POST.get("topic")
        duration = request.POST.get("duration")

        if not topic:
            messages.error(request, "Musisz wpisać temat lekcji!")
            return redirect('generate_lesson')

        # Generowanie treści lekcji przez OpenAI
        lesson_text = generate_lesson_with_openai(topic, duration)

        # Zwiększenie licznika użycia lekcji
        usage.used_lessons += 1
        usage.save()

        # Zapis lekcji do bazy
        lesson = GeneratedLesson.objects.create(
            user=request.user,
            topic=topic,
            duration=int(duration),
            content=lesson_text
        )

        # Zachowaj max 25 ostatnich lekcji
        lessons_to_keep = GeneratedLesson.objects.filter(user=request.user).order_by('-created_at')
        if lessons_to_keep.count() > 25:
            for old_lesson in lessons_to_keep[25:]:
                old_lesson.delete()

        # Czyszczenie Markdown / nagłówków, pozostawiamy czysty tekst
        lesson_html = clean_text(lesson.content)

        return render(request, 'lesson_result.html', {
            "lesson": lesson,
            "topic": topic,
            "duration": duration,
            "lesson_html": lesson_html
        })

    # GET – wyświetlenie formularza do generowania lekcji
    return render(request, 'generate_lesson.html')




# ---------------------
# GENEROWANIE QUIZU
# ---------------------
@login_required(login_url='/login/')
def generate_quiz_from_lesson(request, lesson_id):
    lesson = get_object_or_404(GeneratedLesson, id=lesson_id, user=request.user)

    if request.method == "POST":
        try:
            num_questions = int(request.POST.get("num_questions", 5))
        except ValueError:
            messages.error(request, "Nieprawidłowa liczba pytań!")
            return redirect('view_generated_lessons')

        prompt = f"Stwórz sprawdzian z {num_questions} pytań na podstawie tej lekcji:\n{lesson.content}"

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            quiz_text = str(response.choices[0].message.content)
        except Exception as e:
            error_msg = str(e).encode('utf-8', 'replace').decode('utf-8')
            messages.error(request, "Błąd przy generowaniu quizu: " + error_msg)
            return redirect('view_generated_lessons')

        # Zapis do bazy
        quiz = Quiz.objects.create(
            user=request.user,
            lesson=lesson,
            content=quiz_text
        )

        # 🔹 NOWOŚĆ: przekierowanie od razu do edycji/drukowania PDF
        return redirect('edit_and_download_quiz', quiz_id=quiz.id)

    # GET – pokaz formularz generowania quizu
    return render(request, "generate_quiz_form.html", {"lesson": lesson})

# ---------------------
# POZOSTAŁE WIDOKI
# ---------------------
@login_required(login_url='/login/')
def view_generated_lessons(request):
    lessons = GeneratedLesson.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'view_generated_lessons.html', {"lessons": lessons})

@login_required(login_url="/login/")
def generate_quiz_previous(request):
    lessons = GeneratedLesson.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, "generate_quiz_previous.html", {"lessons": lessons})

@login_required(login_url='/login/')
def generate_quiz_last3(request):
    lessons = GeneratedLesson.objects.filter(user=request.user).order_by('-created_at')[:3]

    if request.method == "POST":
        num_questions = int(request.POST.get("num_questions", 10))
        combined_content = "\n\n".join([l.content for l in lessons])
        prompt = f"Stwórz sprawdzian z {num_questions} pytań na podstawie tych lekcji:\n{combined_content}"

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            quiz_text = str(response.choices[0].message.content)
        except Exception as e:
            messages.error(request, "Błąd przy generowaniu quizu: " + str(e))
            return redirect('dashboard')

        quiz = Quiz.objects.create(user=request.user, content=quiz_text)
        return redirect('edit_and_download_quiz', quiz_id=quiz.id)

    return render(request, "generate_quiz_last3.html", {"lessons": lessons})



#@login_required(login_url="/login/")
#def print_lesson(request):
#    return render(request, "print_lesson.html")


@login_required(login_url="/login/")
def check_generated_lessons(request):
    return render(request, "check_generated_lessons.html")

@login_required(login_url="/login/")
def check_generated_quizzes(request):
    return render(request, "check_generated_quizzes.html")

@login_required(login_url="/login/")
def check_printed_lessons(request):
    return render(request, "check_printed_lessons.html")

# ---------------------
# PDF GENERATOR
# ---------------------
@login_required(login_url='/login/')
def edit_and_download_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)

    # Styl dla Paragraph z UTF-8
    styles = getSampleStyleSheet()
    utf8_style = ParagraphStyle(
        'UTF8',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=12,
        leading=15,
        alignment=TA_LEFT
    )

    # ----------------------
    # Funkcja czyszcząca Markdown ze sprawdzianu
    # ----------------------
    def clean_quiz_text(text):
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()

            # Usuń nagłówki #
            while line.startswith("#"):
                line = line.lstrip("#").strip()

            # Usuń pogrubienia **
            line = line.replace("**", "")

            # Usuń linie poziome ---
            if line.startswith("---"):
                continue

            # Dodaj tylko niepuste linie
            if line:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    # ----------------------
    # Funkcja generująca PDF
    # ----------------------
    def generate_pdf(content):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        story = []

        cleaned_content = clean_quiz_text(content)

        for line in cleaned_content.split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), utf8_style))
                story.append(Spacer(1, 5))  # odstęp między liniami

        doc.build(story)
        buffer.seek(0)
        return buffer

    # ----------------------
    # PDF do podglądu (GET ?pdf=1)
    # ----------------------
    if request.GET.get("pdf") == "1":
        buffer = generate_pdf(quiz.content)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="quiz_{quiz.id}.pdf"'
        return response

    # ----------------------
    # PDF po edycji treści
    # ----------------------
    if request.method == "POST":
        content = request.POST.get("content")
        quiz.content = content
        quiz.save()
        buffer = generate_pdf(content)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="quiz_{quiz.id}.pdf"'
        return response

    # ----------------------
    # Render strony do edycji treści
    # ----------------------
    return render(request, "edit_quiz.html", {"quiz": quiz})




@login_required(login_url='/login/')
def print_lesson_dashboard(request):
    lessons = GeneratedLesson.objects.filter(user=request.user).order_by('-created_at')[:10]
    quizzes = Quiz.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, "print_lesson_dashboard.html", {
        "lessons": lessons,
        "quizzes": quizzes
    })


@login_required(login_url='/login/')
def edit_and_download_lesson(request, lesson_id):
    lesson = get_object_or_404(GeneratedLesson, id=lesson_id, user=request.user)
    return render(request, "edit_lesson.html", {"lesson": lesson})

@login_required(login_url='/login/')
def edit_and_download_lesson(request, lesson_id):
    lesson = get_object_or_404(GeneratedLesson, id=lesson_id, user=request.user)

    # Styl dla Paragraph z UTF-8 (DejaVuSans obsługuje polskie znaki)
    styles = getSampleStyleSheet()
    utf8_style = ParagraphStyle(
        'UTF8',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=12,
        leading=15
    )

    # Funkcja generująca PDF
    def generate_pdf(content):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        # Czyszczenie treści przed PDF
        cleaned_content = clean_text(content)

        story = []
        for line in cleaned_content.split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), utf8_style))
                story.append(Spacer(1, 5))  # odstęp między liniami

        doc.build(story)
        buffer.seek(0)
        return buffer

    # PDF tylko do podglądu (GET ?pdf=1)
    if request.GET.get("pdf") == "1":
        buffer = generate_pdf(lesson.content)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="lesson_{lesson.id}.pdf"'
        return response

    # PDF po edycji treści
    if request.method == "POST":
        content = request.POST.get("content")
        lesson.content = content
        lesson.save()
        buffer = generate_pdf(content)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="lesson_{lesson.id}.pdf"'
        return response

    # Render strony do edycji treści
    return render(request, "edit_lesson.html", {"lesson": lesson})





@login_required(login_url='/login/')
def generate_quiz_multiple_view(request):
    # Pobierz ostatnie 15 lekcji użytkownika
    lessons = GeneratedLesson.objects.filter(user=request.user).order_by('-created_at')[:15]

    if request.method == "POST":
        selected_ids = request.POST.getlist("lessons")
        num_questions = request.POST.get("num_questions")

        if not selected_ids:
            messages.error(request, "Musisz zaznaczyć przynajmniej jedną lekcję!")
            return redirect('generate_quiz_multiple')

        try:
            num_questions = int(num_questions)
            if num_questions > 35:
                messages.error(request, "Maksymalna liczba pytań to 35!")
                return redirect('generate_quiz_multiple')
        except ValueError:
            messages.error(request, "Nieprawidłowa liczba pytań!")
            return redirect('generate_quiz_multiple')

        # Pobranie wybranych lekcji
        selected_lessons = GeneratedLesson.objects.filter(id__in=selected_ids, user=request.user)
        combined_content = "\n\n".join([l.content for l in selected_lessons])

        # Przygotowanie promptu do OpenAI
        prompt = f"Stwórz sprawdzian z {num_questions} pytań na podstawie tych lekcji:\n{combined_content}"

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            quiz_text = str(response.choices[0].message.content)
        except Exception as e:
            messages.error(request, "Błąd przy generowaniu quizu: " + str(e))
            return redirect('generate_quiz_multiple')

        # 🔹 Tworzymy quiz i przypisujemy pierwszą zaznaczoną lekcję, ale treść obejmuje wszystkie wybrane lekcje
        quiz = Quiz.objects.create(
            user=request.user,
            lesson=selected_lessons.first(),  # obowiązkowe dla NOT NULL
            content=quiz_text
        )

        return redirect('edit_and_download_quiz', quiz_id=quiz.id)

    # GET – renderowanie formularza z listą lekcji
    return render(request, "generate_quiz_multiple.html", {"lessons": lessons})






@login_required(login_url='/login/')
def set_quiz_questions_view(request):
    lesson_ids = request.session.get('selected_lesson_ids', [])
    if not lesson_ids:
        messages.error(request, "Brak wybranych lekcji!")
        return redirect('generate_quiz_selected')

    lessons = GeneratedLesson.objects.filter(id__in=lesson_ids, user=request.user)

    if request.method == "POST":
        try:
            num_questions = int(request.POST.get("num_questions", 5))
        except ValueError:
            messages.error(request, "Nieprawidłowa liczba pytań!")
            return redirect('set_quiz_questions')
        
        if num_questions > 35:
            messages.error(request, "Maksymalnie 35 pytań!")
            return redirect('set_quiz_questions')

        # Łączenie treści wszystkich lekcji
        combined_content = "\n\n".join([lesson.content for lesson in lessons])

        prompt = f"Stwórz sprawdzian z {num_questions} pytań na podstawie tych lekcji:\n{combined_content}"

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            quiz_text = str(response.choices[0].message.content)
        except Exception as e:
            error_msg = str(e).encode('utf-8', 'replace').decode('utf-8')
            messages.error(request, "Błąd przy generowaniu quizu: " + error_msg)
            return redirect('generate_quiz_selected')

        # Zapis do bazy – quiz powiązany z pierwszą lekcją (dla prostoty)
        quiz = Quiz.objects.create(
            user=request.user,
            lesson=lessons[0],
            content=quiz_text
        )

        # Przekierowanie od razu do edycji/drukowania w nowej karcie
        return redirect('edit_and_download_quiz', quiz_id=quiz.id)

    return render(request, "set_quiz_questions.html", {"lessons": lessons})


@login_required(login_url="/login/")
def calendar_view(request):
    events = CalendarEvent.objects.filter(user=request.user).order_by('date')

    if request.method == "POST":
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, "Wydarzenie zostało dodane!")
            return redirect('calendar_view')
    else:
        form = CalendarEventForm()

    return render(request, "calendar.html", {"events": events, "form": form})


@login_required(login_url="/login/")
def edit_event_view(request, event_id):
    event = get_object_or_404(CalendarEvent, id=event_id, user=request.user)
    if request.method == "POST":
        form = CalendarEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Wydarzenie zostało zaktualizowane.")
            return redirect('calendar_view')
    else:
        form = CalendarEventForm(instance=event)
    return render(request, "edit_event.html", {"form": form, "event": event})


@login_required(login_url="/login/")
def delete_event_view(request, event_id):
    event = get_object_or_404(CalendarEvent, id=event_id, user=request.user)
    event.delete()
    messages.success(request, "Wydarzenie zostało usunięte.")
    return redirect('calendar_view')





@login_required(login_url='/login/')
def class_dashboard(request):
    classes = SchoolClass.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "class_dashboard.html", {"classes": classes})


@login_required(login_url='/login/')
def create_class(request):
    if request.method == "POST":
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            school_class = form.save(commit=False)
            school_class.user = request.user
            school_class.save()
            messages.success(request, "Klasa została utworzona!")
            return redirect('class_dashboard')
    else:
        form = SchoolClassForm()
    return render(request, "create_class.html", {"form": form})


@login_required(login_url='/login/')
def view_class(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id, user=request.user)
    lessons = GeneratedLesson.objects.filter(user=request.user)

    if request.method == "POST":
        form = AddLessonToClassForm(request.POST)
        form.fields['lesson'].queryset = lessons
        if form.is_valid():
            lesson = form.cleaned_data['lesson']
            ClassLesson.objects.create(school_class=school_class, lesson=lesson)
            messages.success(request, f"Lekcja '{lesson.topic}' dodana do klasy {school_class.name}")
            return redirect('view_class', class_id=class_id)
    else:
        form = AddLessonToClassForm()
        form.fields['lesson'].queryset = lessons

    class_lessons = school_class.lessons.all()

    # obsługa podglądu – jeśli kliknięto "pokaż" przy lekcji
    lesson_preview = None
    lesson_id = request.GET.get("lesson_id")
    if lesson_id:
        try:
            lesson_preview = GeneratedLesson.objects.get(id=lesson_id, user=request.user)
        except GeneratedLesson.DoesNotExist:
            lesson_preview = None

    return render(request, "view_class.html", {
        "school_class": school_class,
        "form": form,
        "class_lessons": class_lessons,
        "lesson_preview": lesson_preview
    })

@login_required(login_url='/login/')
def delete_class(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id, user=request.user)
    school_class.delete()
    messages.success(request, f"Klasa '{school_class.name}' została usunięta.")
    return redirect('class_dashboard')


@login_required(login_url='/login/')
def remove_lesson_from_class(request, class_lesson_id):
    class_lesson = get_object_or_404(ClassLesson, id=class_lesson_id, school_class__user=request.user)
    school_class_id = class_lesson.school_class.id
    class_lesson.delete()
    messages.success(request, "Lekcja została usunięta z klasy.")
    return redirect('view_class', class_id=school_class_id)



def clean_markdown_for_pdf(text):
    """
    Zamienia nagłówki i listy na stylizowany tekst do PDF.
    """
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith("### "):
            cleaned_lines.append(f"<b>{line[4:]}</b><br/>")
        elif line.startswith("#### "):
            cleaned_lines.append(f"<b>{line[5:]}</b><br/>")
        elif line.startswith("- "):
            cleaned_lines.append(f"• {line[2:]}<br/>")
        elif len(line) > 2 and line[:2].isdigit() and line[2] == ".":
            cleaned_lines.append(line + "<br/>")
        else:
            cleaned_lines.append(line + "<br/>")
    return "".join(cleaned_lines)


def clean_text(text):
    """
    Usuwa wszystkie znaki Markdown (#, *, **) i pozostawia czysty tekst.
    Zachowuje listy jako zwykły punkt i numerację jako normalny tekst.
    """
    if not text:
        return ""

    import re

    # Usuń nagłówki Markdown: #, ##, ###, ####
    text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

    # Usuń pogrubienia i kursywy: **tekst**, *tekst*, __tekst__, _tekst_
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)

    # Zamień myślniki listy "- " na punkt •
    text = re.sub(r'^\s*-\s+', '• ', text, flags=re.MULTILINE)

    # Usuń numerowanie typu "1. " na początku linii
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # Usuń nadmiarowe spacje na końcach linii i puste linie
    lines = [line.strip() for line in text.split("\n") if line.strip() != '']

    # Połącz linie w czysty tekst
    return "\n".join(lines)



def clean_quiz_text(text):
    """
    Usuwa wszystkie znaki Markdown z wygenerowanego sprawdzianu:
    - nagłówki (#, ##, ###)
    - pogrubienia (**)
    - linie "---"
    - zachowuje numerację pytań i punktację
    """
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # Usuń nagłówki
        while line.startswith("#"):
            line = line.lstrip("#").strip()

        # Usuń pogrubienia **
        line = line.replace("**", "")

        # Usuń linie poziome
        if line.startswith("---"):
            continue

        # Dodaj tylko niepuste linie
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


from datetime import date
from .models import CalendarEvent

@login_required(login_url='/login/')
def dashboard_view(request):
    today = date.today()
    current_year = today.year
    current_month = today.month
    current_month_name = today.strftime('%B')

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(current_year, current_month)

    # Pobieramy wydarzenia użytkownika w aktualnym miesiącu
    user_events = CalendarEvent.objects.filter(
        user=request.user,
        date__year=current_year,
        date__month=current_month
    )

    # Tworzymy słownik { "YYYY-MM-DD": "tytuł wydarzenia" }
    events_dict = {event.date.strftime("%Y-%m-%d"): event.title for event in user_events}

    calendar_data = []
    for week in month_days:
        week_data = []
        for day in week:
            day_str = day.strftime("%Y-%m-%d")
            if day.month != current_month:
                week_data.append({"day": None, "is_today": False, "event": ""})
            else:
                week_data.append({
                    "day": day.day,
                    "is_today": (day == today),
                    "event": events_dict.get(day_str, "")
                })
        calendar_data.append(week_data)

    # Dodatkowo pobieramy nadchodzące wydarzenia do wyświetlenia pod kalendarzem
    upcoming_events = CalendarEvent.objects.filter(
        user=request.user,
        date__gte=today
    ).order_by('date')[:5]  # np. 5 najbliższych wydarzeń

    return render(request, "dashboard.html", {
        "current_month_name": current_month_name,
        "current_year": current_year,
        "calendar": calendar_data,
        "upcoming_events": upcoming_events,
    })






@login_required
def student_manager(request):
    """Lista klas użytkownika"""
    classes = StudentClass.objects.filter(user=request.user)
    return render(request, 'student_manager.html', {'classes': classes})

@login_required
def create_student_class(request):
    """Tworzenie nowej klasy"""
    if request.method == 'POST':
        form = StudentClassForm(request.POST)
        if form.is_valid():
            student_class = form.save(commit=False)
            student_class.user = request.user
            student_class.save()
            messages.success(request, "Klasa została utworzona.")
            return redirect('student_manager')
    else:
        form = StudentClassForm()
    return render(request, 'create_class2.html', {'form': form})

@login_required
def view_student_class(request, class_id):
    """Widok klasy z uczniami i ich ocenami"""
    student_class = get_object_or_404(StudentClass, id=class_id, user=request.user)
    students = student_class.students.all().prefetch_related('grades')

    student_data = []
    for student in students:
        grades = list(student.grades.all())
        average = None
        if grades:
            total = sum([float(g.value) for g in grades])
            average = round(total / len(grades), 2)
        student_data.append({
            'student': student,
            'grades': grades,
            'average': average
        })

    return render(request, 'view_class2.html', {
        'student_class': student_class,
        'student_data': student_data
    })

@login_required
def add_student(request, class_id):
    """Dodanie ucznia do klasy"""
    student_class = get_object_or_404(StudentClass, id=class_id, user=request.user)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if first_name and last_name:
            Student.objects.create(student_class=student_class, first_name=first_name, last_name=last_name)
        return redirect('view_student_class', class_id=class_id)
    return render(request, 'view_class2.html', {'student_class': student_class})

@login_required
def add_grade(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        value = request.POST.get("value")
        description = request.POST.get("description", "")
        weight = request.POST.get("weight", 1)
        weight_description = request.POST.get("weight_description", "")
        if value:
            grade = Grade.objects.create(
                student=student, 
                value=value, 
                description=description, 
                weight=int(weight), 
                weight_description=weight_description
            )
            # przelicz średnią po dodaniu oceny
            student.average_grade = student.average
            student.save()
    return redirect('class_journal', class_id=student.student_class.id)




from django.shortcuts import render, get_object_or_404, redirect
from .models import StudentClass, Student, Grade

@login_required
def student_manager(request):
    classes = StudentClass.objects.filter(user=request.user)

    if request.method == 'POST':
        class_id = request.POST.get('delete_class_id')
        if class_id:
            school_class = get_object_or_404(StudentClass, id=class_id, user=request.user)
            school_class.delete()
            messages.success(request, f"Klasa '{school_class.name}' została usunięta.")
            return redirect('student_manager')

    return render(request, 'student_manager.html', {'classes': classes})


@login_required
def view_student_class(request, class_id):
    """Widok klasy z uczniami i możliwością dodawania nowego ucznia"""
    student_class = get_object_or_404(StudentClass, id=class_id, user=request.user)
    students = student_class.students.all().prefetch_related('grades')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if first_name and last_name:
            Student.objects.create(student_class=student_class, first_name=first_name, last_name=last_name)
            messages.success(request, f"Uczeń {first_name} {last_name} został dodany.")
            return redirect('view_student_class', class_id=class_id)

    student_data = []
    for student in students:
        grades = list(student.grades.all())
        average = None
        if grades:
            total = sum([float(g.value) for g in grades])
            average = round(total / len(grades), 2)
        student_data.append({
            'student': student,
            'grades': grades,
            'average': average
        })

    return render(request, 'view_class2.html', {
        'student_class': student_class,
        'student_data': student_data
    })




@login_required
def class_journal_view(request, class_id):
    student_class = get_object_or_404(StudentClass, id=class_id, user=request.user)
    students = student_class.students.all().prefetch_related('grades')

    student_data = []
    for student in students:
        grades = list(student.grades.all())
        average = None
        if grades:
            total = sum([float(g.value) for g in grades])
            average = round(total / len(grades), 2)
        student_data.append({
            'student': student,
            'grades': grades,
            'average': average
        })

    return render(request, 'class_journal.html', {
        'student_class': student_class,
        'student_data': student_data
    })





@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id, student_class__user=request.user)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Ucznia zaktualizowano!")
            return redirect('view_student_class', class_id=student.student_class.id)
    else:
        form = StudentForm(instance=student)
    return render(request, 'edit_student.html', {'form': form, 'student': student})

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id, student_class__user=request.user)
    class_id = student.student_class.id
    student.delete()
    messages.success(request, "Ucznia usunięto!")
    return redirect('view_student_class', class_id=class_id)


@login_required
def edit_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id, student__student_class__user=request.user)
    if request.method == "POST":
        value = request.POST.get("value")
        description = request.POST.get("description")
        weight = request.POST.get("weight")
        if value and weight:
            grade.value = float(value)
            grade.description = description
            grade.weight = int(weight)
            grade.save()
            messages.success(request, "Ocena została zaktualizowana.")
            return redirect('class_journal', class_id=grade.student.student_class.id)
    return render(request, "edit_grade.html", {"grade": grade})

@login_required
def delete_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id, student__student_class__user=request.user)
    class_id = grade.student.student_class.id
    grade.delete()
    messages.success(request, "Ocena została usunięta.")
    return redirect('class_journal', class_id=class_id)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import openai
import docx2txt
import PyPDF2
from weasyprint import HTML, CSS

@login_required(login_url="/login/")
def reading_comprehension_view(request):
    generated = None
    article_text = ""
    open_questions = 12
    mc_questions = 15

    if request.method == "POST":
        article_text = request.POST.get("article_text", "").strip()
        open_questions = int(request.POST.get("open_questions", 12))
        mc_questions = int(request.POST.get("mc_questions", 15))
        uploaded_file = request.FILES.get("file")

        # 🔸 Jeśli użytkownik wrzucił plik
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".txt"):
                    article_text = uploaded_file.read().decode("utf-8")
                elif uploaded_file.name.endswith(".docx"):
                    article_text = docx2txt.process(uploaded_file)
                elif uploaded_file.name.endswith(".pdf"):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    article_text = "\n".join([page.extract_text() for page in pdf_reader.pages])
                else:
                    messages.error(request, "Nieobsługiwany format pliku. Użyj .txt, .docx lub .pdf")
            except Exception as e:
                messages.error(request, f"Błąd przy wczytywaniu pliku: {e}")

        if not article_text:
            messages.error(request, "Wklej tekst lub załaduj plik.")
        else:
            # 🔹 Tworzymy prompt
            prompt = f"""
Jesteś nauczycielem. Przygotuj ćwiczenie z czytania ze zrozumieniem
na podstawie poniższego tekstu:

{article_text}

Wygeneruj:
1️⃣ Krótkie streszczenie tekstu.
2️⃣ {open_questions} pytań otwartych (open-ended).
3️⃣ {mc_questions} pytań wielokrotnego wyboru z trzema opcjami odpowiedzi.
4️⃣ Klucz odpowiedzi.
"""

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful educational assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                generated = response.choices[0].message.content
            except Exception as e:
                messages.error(request, f"Błąd generowania: {e}")

        # 🔹 Pobieranie PDF
        if request.POST.get("download_pdf"):
            pdf_content = request.POST.get("generated_text", generated)
            html_string = f"""
<html>
<head>
<meta charset="UTF-8">
<style>
@page {{ size: A4; margin: 2cm; }}
body {{ font-family: Arial, sans-serif; font-size: 10pt; line-height: 1.4; }}
h1 {{ font-size: 12pt; color: #333; }}
pre {{ white-space: pre-wrap; word-wrap: break-word; font-size: 10pt; }}
</style>
</head>
<body>
<h1>Ćwiczenie z czytania ze zrozumieniem</h1>
<pre>{pdf_content}</pre>
</body>
</html>
"""
            pdf_file = HTML(string=html_string).write_pdf(stylesheets=[CSS(string="body { font-family: Arial; }")])
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="reading_comprehension.pdf"'
            return response

    return render(request, "reading_comprehension.html", {
        "generated": generated,
        "article_text": article_text,
        "open_questions": open_questions,
        "mc_questions": mc_questions,
    })


