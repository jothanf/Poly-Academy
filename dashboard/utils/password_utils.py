import random
import string

def generate_secure_password(username, length=12):
    """
    Genera una contraseña segura basada en el nombre de usuario
    """
    # Usar parte del username como base
    base = username[:4] if len(username) >= 4 else username
    
    # Caracteres para hacer la contraseña más segura
    special_chars = "!@#$%&*"
    numbers = string.digits
    letters = string.ascii_letters
    
    # Construir la contraseña
    password = (
        base.capitalize() + 
        ''.join(random.choice(letters) for _ in range(3)) +
        ''.join(random.choice(numbers) for _ in range(3)) +
        random.choice(special_chars) +
        ''.join(random.choice(letters + numbers + special_chars) for _ in range(2))
    )
    
    # Mezclar la contraseña final
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list) 