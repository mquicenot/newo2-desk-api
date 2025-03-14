from neo4j_manager.models.wallet import obtener_metodos_pago, eliminar_tarjeta
from neo4j_manager.driver import Neo4jDriver

class Neo4jWallet:
    """
    Procesar solicitudes POST de usuarios para creación en Neo4j.
    """

    def __init__(self):
        """
        Constructor de la clase. Inicializa las conexiones a la base de datos.
        """
        self.db = Neo4jDriver()

    def ObtenerWallet(self, user_data):
        """
        Método para crear un nuevo usuario en la base de datos Neo4j.

        :param user_data: Diccionario que contiene la información del usuario a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    result = obtener_metodos_pago(user_data, tx)
                    tx.commit()
                    print('✔ Usuario creado correctamente: ', result)
                    return result
                except Exception as e:
                    tx.rollback()
                finally:
                    self.db.close()
    
    def EliminarTarjeta(self, user_data):
        """
        Método para crear un nuevo usuario en la base de datos Neo4j.

        :param user_data: Diccionario que contiene la información del usuario a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    result = eliminar_tarjeta(user_data, tx)
                    tx.commit()
                    print('✔ Usuario creado correctamente: ', result)
                    return result
                except Exception as e:
                    tx.rollback()
                finally:
                    self.db.close()
    
    