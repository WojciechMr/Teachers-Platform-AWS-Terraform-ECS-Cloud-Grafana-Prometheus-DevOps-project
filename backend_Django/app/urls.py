from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health),  # opcjonalne, middleware i tak zwraca 200
    path("", views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

  # Generowanie lekcji
    path("generate-lesson/", views.generate_lesson_view, name="generate_lesson"),

    # Generowanie sprawdzianów
    path("generate_quiz_previous/", views.generate_quiz_previous, name="generate_quiz_previous"),
    path("generate_quiz_last3/", views.generate_quiz_last3, name="generate_quiz_last3"),

    # Podsumowania / drukowanie
    #path("print_lesson/", views.print_lesson, name="print_lesson"),


    # Widoki sprawdzające zasoby
    path("check_generated_lessons/", views.check_generated_lessons, name="check_generated_lessons"),
    path("check_generated_quizzes/", views.check_generated_quizzes, name="check_generated_quizzes"),
    path("check_printed_lessons/", views.check_printed_lessons, name="check_printed_lessons"),
    path('generated-lessons/', views.view_generated_lessons, name='view_generated_lessons'),
    path('generate_quiz/<int:lesson_id>/', views.generate_quiz_from_lesson, name='generate_quiz_from_lesson'),
    path('edit_lesson/<int:lesson_id>/', views.edit_and_download_lesson, name='edit_and_download_lesson'),
    path("print_lesson/", views.print_lesson_dashboard, name="print_lesson"),
    path('edit_quiz/<int:quiz_id>/', views.edit_and_download_quiz, name='edit_and_download_quiz'),
    path("print_lesson/", views.print_lesson_dashboard, name="print_lesson_dashboard"),
    #path('generate_quiz_selected/', views.generate_quiz_selected_lessons_view, name='generate_quiz_selected'),
    path('set_quiz_questions/', views.set_quiz_questions_view, name='set_quiz_questions'),
    path('generate_quiz_multiple/', views.generate_quiz_multiple_view, name='generate_quiz_multiple'),
    path("calendar/", views.calendar_view, name="calendar_view"),
    path("calendar/edit/<int:event_id>/", views.edit_event_view, name="edit_event"),
    path("calendar/delete/<int:event_id>/", views.delete_event_view, name="delete_event"),
    path("classes/", views.class_dashboard, name="class_dashboard"),
    path("classes/create/", views.create_class, name="create_class"),
    path("classes/<int:class_id>/", views.view_class, name="view_class"),
    path('class_lesson/remove/<int:class_lesson_id>/', views.remove_lesson_from_class, name='remove_lesson_from_class'),
    path('students/', views.student_manager, name='student_manager'),
    path('students/create/', views.create_student_class, name='create_student_class'),
    path('students/class/<int:class_id>/', views.view_student_class, name='view_student_class'),
    path('students/class/<int:class_id>/add_student/', views.add_student, name='add_student'),
    path('students/student/<int:student_id>/add_grade/', views.add_grade, name='add_grade'),
    path('students/class/<int:class_id>/journal/', views.class_journal_view, name='class_journal'),
    path('students/class/<int:class_id>/journal/', views.class_journal_view, name='class_journal_view'),
    path('students/class/<int:class_id>/', views.view_student_class, name='view_student_class'),
    path('students/student/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('students/student/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('grade/<int:grade_id>/edit/', views.edit_grade, name='edit_grade'),
    path('grade/<int:grade_id>/delete/', views.delete_grade, name='delete_grade'),
    path("reading-comprehension/", views.reading_comprehension_view, name="reading_comprehension"),
    path('classes/<int:class_id>/delete/', views.delete_class, name='delete_class'),
    






    

]