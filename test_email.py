import smtplib
from email.mime.text import MIMEText

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "Edublinkier@gmail.com"  # Twój Gmail
EMAIL_HOST_PASSWORD = "gekm mdvr eqwk bidf"


# Treść wiadomości
msg = MIMEText("To jest testowa wiadomość.")
msg["Subject"] = "Test SMTP"
msg["From"] = EMAIL_HOST_USER
msg["To"] = "wojtekmrozek717@gmail.com"  # odbiorca

try:
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    server.starttls()
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    server.send_message(msg)
    server.quit()
    print("Wiadomość wysłana pomyślnie!")
except Exception as e:
    print("Błąd SMTP:", e)
