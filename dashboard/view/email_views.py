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


destinatarios = [
    'jothanferney@gmail.com',
]

sends_cuantity = 0
address_sends = []

# Contenido del correo de prueba
contenido_html = """
<html>
<body>
    <h1>Correo de Prueba</h1>
    <p>Este es un correo de prueba enviado desde Python.</p>
</body>
</html>
"""

# Modificar el código de envío de correo
for destinatario in destinatarios:
    msg = MIMEMultipart()  # Cambiamos a MIMEMultipart simple
    msg['Subject'] = asunto
    msg['From'] = remitente
    msg['To'] = destinatario

    # Crear la parte HTML del mensaje
    html_part = MIMEText(contenido_html, 'html')
    msg.attach(html_part)

    try:
        # Enviar el correo
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Imprimir para debug (eliminar en producción)
        print(f"Intentando autenticar con: {remitente}")
        
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        sends_cuantity += 1
        address_sends.append(destinatario)
        print(f"Correo enviado exitosamente a {destinatario}")
    except Exception as e:
        print(f"Error al enviar el correo a {destinatario}: {str(e)}")

print(address_sends)

def send_welcome_email(destinatario, username, password):
    """
    Envía un correo de bienvenida con las credenciales del usuario
    """
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
        msg = MIMEMultipart()
        msg['Subject'] = asunto
        msg['From'] = remitente
        msg['To'] = destinatario

        html_part = MIMEText(contenido_html, 'html')
        msg.attach(html_part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        logger.error(f"Error enviando email de bienvenida a {destinatario}: {str(e)}")
        return False