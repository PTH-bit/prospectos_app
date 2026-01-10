"""
Utilidades para envío de emails en el CRM ZARITA!
"""

import smtplib
from email.mime.text import MIMEText


def enviar_notificacion_email(destinatario: str, asunto: str, cuerpo: str):
    """Envía una notificación por correo electrónico (Simulado por ahora)"""
    try:
        # En un entorno real, aquí se configurarían las credenciales SMTP
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login("zaritahouse@gmail.com", "Travel2026/*")
        # msg = MIMEText(cuerpo)
        # msg['Subject'] = asunto
        # msg['From'] = "sistema@prospectos.com"
        # msg['To'] = destinatario
        # server.send_message(msg)
        # server.quit()
        print(f"📧 [EMAIL SIMULADO] A: {destinatario} | Asunto: {asunto}")
        return True
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False
