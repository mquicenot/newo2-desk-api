from neo4j_manager.models.compras import compra_ilimitado_individual, compra_ilimitado_equipo, compra_membresia_equipo, obtener_compras
from neo4j_manager.driver import Neo4jDriver

class Neo4jCompras:
    """
    Procesar solicitudes POST de usuarios para creación en Neo4j.
    """

    def __init__(self):
        """
        Constructor de la clase. Inicializa las conexiones a la base de datos.
        """
        self.db = Neo4jDriver()

    def IlimitadoIndividual(self, user_data):
        """
        Método para crear un nuevo usuario en la base de datos Neo4j.

        :param user_data: Diccionario que contiene la información del usuario a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    print( 'estoy entrando a la funcion')
                    result = compra_ilimitado_individual(user_data, tx)
                    tx.commit()
                    print('✔ Usuario creado correctamente: ', result)
                    return result
                except Exception as e:
                    tx.rollback()
                finally:
                    self.db.close()
    
    def IlimitadoEquipo(self, user_data):
        """
        Método para crear un nuevo usuario en la base de datos Neo4j.

        :param user_data: Diccionario que contiene la información del usuario a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    print( 'estoy entrando a la funcion')
                    result = compra_ilimitado_equipo(user_data, tx)
                    tx.commit()
                    print('✔ Usuario creado correctamente: ', result)
                    return result
                except Exception as e:
                    tx.rollback()
                finally:
                    self.db.close()


    def MembresiaEquipo(self, user_data):
        """
        Método para crear un nuevo usuario en la base de datos Neo4j.

        :param user_data: Diccionario que contiene la información del usuario a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    print( 'estoy entrando a la funcion')
                    result = compra_membresia_equipo(user_data, tx)
                    tx.commit()
                    print('✔ Usuario creado correctamente: ', result)
                    return result
                except Exception as e:
                    tx.rollback()
                finally:
                    self.db.close()
    
    def ObtenerCompras(self, user_data):
        """
        Método obtener compras.

        :param user_data: Diccionario que contiene la información del usuario a crear.
        """
        driver = self.db.connect()
        with driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    print( 'estoy entrando a la funcion')
                    result = obtener_compras(user_data, tx)
                    tx.commit()
                    return result
                except Exception as e:
                    tx.rollback()
                finally:
                    self.db.close()