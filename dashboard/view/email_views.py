import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

import csv
import logging

logger = logging.getLogger(__name__)

# Crear una lista vacía para almacenar los correos electrónicos
correos_list = []


load_dotenv() # CArga las variables de entorno desde el archivo .env

remitente = os.getenv('USER_EMAIL')
password = os.getenv('USER_PASSWORD_EMAIL')

if not remitente or not password:
    raise ValueError("Las credenciales de correo (USER y PASS) no están configuradas en el archivo .env")

# Modificar la creación del asunto para evitar problemas de codificación
asunto = "PolyAcademy email"  # Simplificamos el asunto sin usar Header


# Eliminar la lista de destinatarios y el código de prueba que está enviando correos genéricos

def send_welcome_email(destinatario, username, password):
    """
    Envía un correo de bienvenida con las credenciales del usuario
    """
    logger.info(f"Iniciando envío de email de bienvenida para: {destinatario}")
    asunto = "Bienvenido a PolyAcademy - Tus credenciales de acceso"
    
    contenido_html = f"""
    <html>
    <body>
        <h1>¡Bienvenido a PolyAcademy!</h1>
        <p>Tu cuenta ha sido creada exitosamente.</p>
        <p>Tus credenciales de acceso son:</p>
        <ul>
            <li><strong>Usuario:</strong> {username}</li>
            <li><strong>Contraseña:</strong> {password}</li>
        </ul>
        <p>Por favor, cambia tu contraseña la primera vez que inicies sesión.</p>
        <p>¡Gracias por unirte a nuestra plataforma!</p>
    </body>
    </html>
    """

    try:
        logger.debug(f"Configurando mensaje para: {destinatario}")
        msg = MIMEMultipart()
        msg['Subject'] = asunto
        msg['From'] = remitente
        msg['To'] = destinatario

        html_part = MIMEText(contenido_html, 'html')
        msg.attach(html_part)

        logger.debug("Iniciando conexión SMTP")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        logger.debug(f"Intentando autenticar con email: {remitente}")
        server.login(remitente, os.getenv('USER_PASSWORD_EMAIL'))  # Usar la contraseña correcta del email
        
        logger.debug("Enviando email...")
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        logger.info(f"Email enviado exitosamente a: {destinatario}")
        
        return True
    except Exception as e:
        logger.error(f"Error detallado enviando email a {destinatario}: {str(e)}")
        return False

def send_reset_code_email(destinatario, codigo):
    """
    Envía un correo con el código de recuperación de contraseña
    """
    asunto = "Código de recuperación de contraseña - PolyAcademy"
    
    contenido_html = f"""
    <html>
    <body>
        <h1>Recuperación de contraseña</h1>
        <p>Has solicitado recuperar tu contraseña en PolyAcademy.</p>
        <p>Tu código de recuperación es: <strong>{codigo}</strong></p>
        <p>Este código expirará en 1 hora.</p>
        <p>Si no solicitaste este cambio, ignora este correo.</p>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart()
        msg['Subject'] = asunto
        msg['From'] = remitente
        msg['To'] = destinatario

        html_part = MIMEText(contenido_html, 'html')
        msg.attach(html_part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, os.getenv('USER_PASSWORD_EMAIL'))
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        logger.error(f"Error enviando email de recuperación a {destinatario}: {str(e)}")
        return False