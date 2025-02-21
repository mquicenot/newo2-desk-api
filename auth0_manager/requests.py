import requests
from fastapi import HTTPException
from auth0.v3.authentication import GetToken
from dotenv import load_dotenv
import os

# Carga las variables de entorno desde el archivo .env
load_dotenv()

class auth0Services:
    """
    Clase para interactuar con los servicios de Auth0, como obtener tokens de acceso y crear usuarios.
    """

    def __init__(self):
        """
        Inicializa la clase con las credenciales de Auth0 obtenidas de las variables de entorno.
        
        La URL base, el ID de cliente, el secreto de cliente, y otros parámetros necesarios para la autenticación
        son leídos desde el archivo .env.
        """
        # Obtener valores de las variables de entorno
        self.base_url = os.getenv('AUTH0_ISSUER')
        self.client_id = os.getenv('AUTH0_CLIENT_ID')
        self.domain = os.getenv('AUTH0_DOMAIN')
        self.client_secret = os.getenv('AUTH0_CLIENT_SECRET')
        self.audience = os.getenv('AUTH0_API_AUDIENCE')
    
    def get_access_token(self, username: str, password: str):
        """
        Obtiene un token de acceso de Auth0 usando el flujo de autenticación por nombre de usuario y contraseña.

        Parámetros:
        - username (str): El nombre de usuario para la autenticación.
        - password (str): La contraseña del usuario.

        Retorna:
        - dict: Un diccionario que contiene el token de acceso de Auth0. Ejemplo: {"access_token": "abc123"}.
        
        Si ocurre un error durante la autenticación, se captura y maneja la excepción HTTPException o Exception.
        """
        try:
            # Limpia el nombre de usuario eliminando espacios y convirtiéndolo a minúsculas
            cleaned_username = username.strip().lower()
            
            # Crear instancia de GetToken de la librería Auth0
            auth0 = GetToken(self.domain)
            
            # Realizar el login usando el método login de Auth0
            token_response = auth0.login(
                client_id=self.client_id,
                client_secret=self.client_secret,
                audience=self.audience,
                username=cleaned_username,
                password=password,
                realm='Username-Password-Authentication',
                grant_type='password',
                scope='openid profile email'
            )
            
            # Retorna el token de acceso en formato JSON
            return {"access_token": token_response['access_token']}
        
        except HTTPException as e:
            # Si ocurre una excepción HTTP (por ejemplo, credenciales incorrectas), se captura y se retorna una excepción HTTP personalizada
            print(f"HTTPException: {e}")
            return HTTPException(status_code=400, detail=e)
        
        except Exception as e:
            # Si ocurre cualquier otra excepción (por ejemplo, problemas de red), se captura y se lanza un error HTTP 500
            print(f"Error: {str(e)}")  # Imprimir el error completo para depuración
            raise HTTPException(status_code=500, detail=str(e))

    def create_new_user(self, username: str, password: str):
        """
        Crea un nuevo usuario en Auth0 con el nombre de usuario y la contraseña proporcionados.

        Parámetros:
        - username (str): El nombre de usuario para el nuevo usuario.
        - password (str): La contraseña del nuevo usuario.

        Retorna:
        - dict: Un diccionario con un mensaje de éxito si el usuario es creado correctamente. Ejemplo: {"mensaje": "El usuario ha sido creado"}.
        
        Si ocurre un error durante la creación del usuario, se captura y maneja la excepción, pero no se lanza.
        """
        # Construir la URL para la creación de usuarios en Auth0
        url = f"{self.base_url}/dbconnections/signup"
        
        # Inicializar los encabezados (por ahora está vacío, pero podría contener tokens de autenticación, etc.)
        headers = {}

        # Limpia el nombre de usuario y lo prepara para la solicitud
        cleaned_username = username.strip().lower()
        
        # Datos que se enviarán en el cuerpo de la solicitud POST para crear un nuevo usuario
        data = {
            "client_id": self.client_id,
            "email": cleaned_username,
            "password": password,
            "connection": "Username-Password-Authentication"  # Usar la conexión de autenticación por nombre de usuario y contraseña
        }

        try:
            # Realizar la solicitud POST para crear el usuario
            response = requests.post(url, json=data, headers=headers)
            
            # Si la respuesta es exitosa (código 2xx), la solicitud se completó correctamente
            response.raise_for_status()  # Esto lanza una excepción si el código de estado es 4xx o 5xx
            
            # Retorna un mensaje de éxito como un diccionario JSON
            return {'mensaje': 'El usuario ha sido creado'}
        
        except Exception as err:
            # Levanta el error HTTP si ocurre un problema
            raise Exception(f"El correo que intentas ingresar ya esta registrado.")
        
    
    def change_password(self, username: str):
        """
        Solicita un cambio de contraseña para un usuario existente en Auth0.

        Parámetros:
        - username (str): El nombre de usuario para el que se solicita el cambio de contraseña.

        Retorna:
        - dict: Un diccionario con un mensaje de éxito si la solicitud fue exitosa.
        
        Si ocurre un error durante la solicitud, se captura y maneja la excepción adecuadamente.
        """
        # Construir la URL para la solicitud de cambio de contraseña en Auth0
        url = f"{self.base_url}/dbconnections/change_password"
        
        # Inicializar los encabezados (por ahora vacío, pero podría contener tokens de autenticación, etc.)
        headers = {}

        # Limpiar el nombre de usuario y prepararlo para la solicitud
        cleaned_username = username.strip().lower()
        
        # Datos que se enviarán en el cuerpo de la solicitud POST para cambiar la contraseña
        data = {
            "client_id": self.client_id,
            "email": cleaned_username,
            "connection": "Username-Password-Authentication"  # Usar la conexión de autenticación por nombre de usuario y contraseña
        }

        try:
            # Realizar la solicitud POST para cambiar la contraseña
            response = requests.post(url, json=data, headers=headers)
            
            # Si la respuesta es exitosa (código 2xx), la solicitud se completó correctamente
            response.raise_for_status()  # Esto lanza una excepción si el código de estado es 4xx o 5xx
            
            # Retorna un mensaje de éxito si la contraseña fue solicitada correctamente
            return {'mensaje': 'Se ha enviado la solicitud de cambio de contraseña. Revisa tu correo electrónico.'}
        
        except requests.exceptions.HTTPError as err:
            # Si ocurre un error HTTP (código 4xx o 5xx), lo manejamos aquí
            # Esto puede incluir errores como usuario no encontrado o problemas en el servidor
            raise Exception(f"Error HTTP: {err.response.status_code}. No se pudo procesar la solicitud.")
        
        except requests.exceptions.RequestException as err:
            # Si ocurre un error en la solicitud (por ejemplo, problemas de red), lo manejamos aquí
            raise Exception(f"Error en la solicitud: {str(err)}. Intenta de nuevo más tarde.")
        
        except Exception as err:
            # Manejo de otros posibles errores generales
            raise Exception(f"Ha ocurrido un error inesperado: {str(err)}. Intenta nuevamente.")