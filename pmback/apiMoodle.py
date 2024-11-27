import requests

class MoodleAPI:
    def __init__(self, base_url, token):
        """
        Inicializa la conexión con Moodle
        """
        self.base_url = base_url
        self.token = token
        self.base_params = {
            'wstoken': self.token,
            'moodlewsrestformat': 'json'
        }

    def get_site_info(self):
        """
        Obtiene información del sitio y verifica la conexión
        """
        params = {
            **self.base_params,
            'wsfunction': 'core_webservice_get_site_info'
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

    def create_user(self, username, firstname, lastname, email, password):
        """
        Crea un nuevo usuario en Moodle
        """
        params = {
            **self.base_params,
            'wsfunction': 'core_user_create_users',
            'users[0][username]': username,
            'users[0][firstname]': firstname,
            'users[0][lastname]': lastname,
            'users[0][email]': email,
            'users[0][password]': password,
            'users[0][auth]': 'manual'
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

    def get_user_by_field(self, field, value):
        """
        Busca usuarios por un campo específico (email, username, etc)
        """
        params = {
            **self.base_params,
            'wsfunction': 'core_user_get_users_by_field',
            'field': field,
            'values[0]': value
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

    def get_users(self, criteria_key, criteria_value):
        """
        Obtiene usuarios basado en criterios
        """
        params = {
            **self.base_params,
            'wsfunction': 'core_user_get_users',
            'criteria[0][key]': criteria_key,
            'criteria[0][value]': criteria_value
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

    def update_user(self, user_id, **user_data):
        """
        Actualiza la información de un usuario
        """
        params = {
            **self.base_params,
            'wsfunction': 'core_user_update_users',
            'users[0][id]': user_id
        }
        
        # Agregar campos a actualizar
        for key, value in user_data.items():
            params[f'users[0][{key}]'] = value

        response = requests.get(self.base_url, params=params)
        return response.json()

    # Funciones de Cursos
    def create_course(self, fullname, shortname, categoryid):
        params = {
            **self.base_params,
            'wsfunction': 'core_course_create_courses',
            'courses[0][fullname]': fullname,
            'courses[0][shortname]': shortname,
            'courses[0][categoryid]': categoryid
        }
        return self._make_request(params)

    # Funciones de Inscripción
    def enrol_user(self, user_id, course_id, role_id=5):  # 5 es el rol de estudiante por defecto
        params = {
            **self.base_params,
            'wsfunction': 'enrol_manual_enrol_users',
            'enrolments[0][userid]': user_id,
            'enrolments[0][courseid]': course_id,
            'enrolments[0][roleid]': role_id
        }
        return self._make_request(params)

    # Funciones de Calificaciones
    def get_course_grades(self, user_id, course_id):
        params = {
            **self.base_params,
            'wsfunction': 'gradereport_user_get_grade_items',
            'userid': user_id,
            'courseid': course_id
        }
        return self._make_request(params)

    # Función auxiliar para hacer requests
    def _make_request(self, params):
        response = requests.get(self.base_url, params=params)
        return response.json()


# Ejemplo de uso:
if __name__ == "__main__":
    # Configuración
    BASE_URL = "https://mypolyacademy.com/idiomas/ingles/webservice/rest/server.php"
    TOKEN = "6087922d5f194b0e15f758af2a03161c"

    # Crear instancia de la API
    moodle = MoodleAPI(BASE_URL, TOKEN)

    try:
        # Verificar conexión
        site_info = moodle.get_site_info()
        print("Conexión exitosa con:", site_info['sitename'])

        # Ejemplo de creación de usuario
        new_user = moodle.create_user(
            username="testuser2",
            firstname="Test",
            lastname="User",
            email="testuser2@example.com",
            password="Test123456!"
        )
        print("Usuario creado:", new_user)

        # Ejemplo de búsqueda de usuario
        user = moodle.get_user_by_field('email', 'testuser2@example.com')
        print("Usuario encontrado:", user)

    except Exception as e:
        print("Error:", str(e))