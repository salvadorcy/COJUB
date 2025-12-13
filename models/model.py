import os
from dotenv import load_dotenv
import pyodbc
from collections import namedtuple

# Definir la estructura de los datos del socio y de configuración
#Socio = namedtuple('Socio', [
#    'FAMID', 'FAMNom', 'FAMAdressa', 'FAMPoblacio', 'FAMCodPos', 'FAMTelefon',
#    'FAMMobil', 'FAMEmail', 'FAMDataAlta', 'FAMCCC', 'FAMIBAN', 'FAMBIC',
#    'FAMNSocis', 'bBaixa', 'FAMObservacions', 'FAMbSeccio', 'FAMNIF',
#    'FAMDataNaixement', 'FAMQuota', 'FAMIDSec', 'FAMDataBaixa', 'FAMTipus',
#    'FAMSexe', 'FAMSociReferencia', 'FAMNewId', 'FAMNewIdRef',
#    'FAMbPagamentDomiciliat', 'FAMbRebutCobrat', 'FAMPagamentFinestreta'
#])

Socio = namedtuple('Socio', [
    'FAMID', 'FAMNom', 'FAMAdressa', 'FAMPoblacio', 'FAMCodPos', 'FAMTelefon',
    'FAMMobil', 'FAMEmail', 'FAMDataAlta', 'FAMIBAN', 'FAMBIC',
    'FAMNSocis', 'bBaixa', 'FAMObservacions', 'FAMNIF',
    'FAMDataNaixement', 'FAMQuota', 'FAMDataBaixa',
    'FAMSexe', 'FAMSociReferencia',
    'FAMbPagamentDomiciliat', 'FAMbRebutCobrat', 'FAMPagamentFinestreta'
])

Dades = namedtuple('Dades', [
    'TotalDefuncions', 'AcumulatDefuncions', 'PreuDerrama', 'ComissioBancaria',
    'IdFactura', 'Presentador', 'CIFPresentador', 'Ordenant', 'CIFOrdenant',
    'IBANPresentador', 'BICPresentador', 'PWD', 'QuotaSocis',
    'SufixeRebuts', 'TexteRebutFinestreta'
])


class DatabaseModel:
    """
    Clase que gestiona la conexión a la base de datos y las operaciones CRUD.
    """
    def __init__(self):
        load_dotenv()
        # NOTA: Debes rellenar esta cadena de conexión con tus propios datos
        self.conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv("SQL_SERVER")};"
            f"DATABASE={os.getenv("SQL_DATABASE")};"
            f"UID={os.getenv("SQL_USER")};"
            f"PWD={os.getenv("SQL_PASSWORD")};"
        )
        self.conn = pyodbc.connect(self.conn_str)

    def connect(self):
        """Establece la conexión a la base de datos."""
        try:
            self.conn = pyodbc.connect(self.conn_str)
            print("Conexión a la base de datos establecida.")
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error de conexión: {sqlstate}")
            raise

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            print("Conexión a la base de datos cerrada.")

    def get_all_socis(self):
        """Recupera todos los socios de la base de datos."""
        query = "SELECT * FROM scazorla_sa.G_Socis"
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return [Socio(*row) for row in cursor.fetchall()]

    def get_dades(self):
        """Recupera los datos de configuración de la tabla G_Dades."""
        query = "SELECT * FROM scazorla_sa.G_Dades"
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
            if row:
                # Se excluye el campo de identidad [RegID]
                return Dades(*row[:-1])
            return None

    def socio_exists(self, fam_id):
        """Verifica si un socio con un FAMID específico ya existe."""
        query = "SELECT FAMID FROM scazorla_sa.G_Socis WHERE FAMID = ?"
        with self.conn.cursor() as cursor:
            cursor.execute(query, fam_id)
            return cursor.fetchone() is not None

    def add_socio(self, data):
        """Añade un nuevo socio a la base de datos."""
        placeholders = ', '.join(['?'] * len(data))
        columns = ', '.join(Socio._fields)
        query = f"INSERT INTO scazorla_sa.G_Socis ({columns}) VALUES ({placeholders})"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, data)
                self.conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al añadir socio: {ex}")
            return False

    def update_socio(self, data):
        """Actualiza un socio existente en la base de datos."""
        fam_id = data[0]
        # Excluir FAMID del SET ya que no se debe actualizar la clave primaria
        update_fields = [f for f in Socio._fields if f != 'FAMID']
        update_pairs = ', '.join([f"{col} = ?" for col in update_fields])
        query = f"UPDATE scazorla_sa.G_Socis SET {update_pairs} WHERE FAMID = ?"
        try:
            with self.conn.cursor() as cursor:
                # Excluir el primer elemento (FAMID) de data y agregar FAMID al final para el WHERE
                ordered_data = data[1:] + (fam_id,)
                cursor.execute(query, ordered_data)
                self.conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al actualizar socio: {ex}")
            return False

    def delete_socio(self, fam_id):
        """Elimina un socio de la base de datos."""
        query = "DELETE FROM scazorla_sa.G_Socis WHERE FAMID = ?"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, fam_id)
                self.conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al eliminar socio: {ex}")
            return False

    def update_dades(self, data):
        """Actualiza los datos de configuración en la base de datos."""
        # Se asume que solo hay una fila, por lo que se actualiza por el ID 1
        # Se excluye el campo de identidad [RegID]
        update_pairs = ', '.join([f"{col} = ?" for col in Dades._fields])
        query = f"UPDATE scazorla_sa.G_Dades SET {update_pairs} WHERE RegID = 1"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, data)
                self.conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al actualizar datos de configuración: {ex}")
            return False