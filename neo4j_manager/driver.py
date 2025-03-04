from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
os.environ.pop("DB_USER", None)
os.environ.pop("DB_PASSWORD", None)
os.environ.pop("DB_HOST", None)
# Cargar las variables del archivo .env
load_dotenv(override=True)

class Neo4jDriver:
    """
    Clase que maneja la conexión con Neo4j y ejecuta consultas en la base de datos.
    """

    def __init__(self):
        """
        Inicializa las variables necesarias para la conexión con Neo4j.
        Carga las credenciales desde el archivo .env.
        """
        self._uri = os.getenv('URI_NEO4J')  
        self._user = os.getenv('USER_NEO4J')  
        self._password = os.getenv('PASSWORD_NEO4J')  
        self._driver = None  

    def connect(self):
        """
        Establece una conexión con la base de datos Neo4j.
        Si no se ha creado aún el driver, lo crea y lo guarda en la variable _driver.
        
        :return: Driver de conexión a Neo4j (GraphDatabase.driver).
        """
        if self._driver is None:  
            try:
                self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))
            except Exception as e:
                return;
        return self._driver  

    def close(self):
        """
        Cierra la conexión con la base de datos Neo4j.
        Si el driver existe, se cierra la conexión.
        """
        if self._driver is not None:  
            self._driver.close()  