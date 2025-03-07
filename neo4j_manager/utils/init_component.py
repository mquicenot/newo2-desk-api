from neo4j_manager.models.init_components import init_components, create_jhi_user_with_miembro
from neo4j_manager.driver import Neo4jDriver

class Neo4jInitComopnents:
    """
    Procesar solicitudes POST de usuarios para creación en Neo4j.
    """

    def __init__(self):
        """
        Constructor de la clase. Inicializa las conexiones a la base de datos.
        """
        self.db = Neo4jDriver()

    def InitComponents(self, user_data):
        """
        Método para crear un nuevo usuario en la base de datos Neo4j.

        :param user_data: Diccionario que contiene la información del usuario a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    result = init_components(user_data, tx)
                    tx.commit()
                    print('✔ Usuario creado correctamente: ', result)
                    return result
                except Exception as e:
                    tx.rollback()
                finally:
                    self.db.close()
    
    def createJhiUserWithMiembro(self, user_data):
        """
        Método para crear un nuevo usuario en la base de datos Neo4j.

        :param user_data: Diccionario que contiene la información del usuario a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    result = create_jhi_user_with_miembro(user_data, tx)
                    tx.commit()
                    print('✔ Usuario creado correctamente: ', result)
                    return result
                except Exception as e:
                    print(f"❌ Error al ejecutar la mutación: {e}")
                    tx.rollback()
                finally:
                    self.db.close() 
                