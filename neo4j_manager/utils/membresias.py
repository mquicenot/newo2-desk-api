from neo4j_manager.models.membresias import obtener_membresias
from neo4j_manager.models.init_components import usuario_info
from neo4j_manager.driver import Neo4jDriver
from auth0_manager.requests import auth0Services
import random
import string


class Neo4jMembresias:
    """
    Procesar solicitudes POST de usuarios para creación en Neo4j.
    """

    def __init__(self):
        """
        Constructor de la clase. Inicializa las conexiones a la base de datos.
        """
        self.db = Neo4jDriver()

    def ObtenerMembresias(self):
        """
        Método para crear un nuevo usuario en la base de datos Neo4j.

        :param user_data: Diccionario que contiene la información del usuario a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    result = obtener_membresias(tx)
                    tx.commit()
                    print('✔ Usuario creado correctamente: ', result)
                    return result
                except Exception as e:
                    print(f"❌ Error al ejecutar la mutación: {e}")
                    tx.rollback()
                finally:
                    self.db.close()
