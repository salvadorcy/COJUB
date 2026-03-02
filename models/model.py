import os
from dotenv import load_dotenv
import pyodbc
from collections import namedtuple
from datetime import datetime
from pathlib import Path


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
    'FAMID',                    # 1
    'FAMNom',                   # 2
    'FAMAdressa',               # 3
    'FAMPoblacio',              # 4
    'FAMCodPos',                # 5
    'FAMTelefon',               # 6
    'FAMMobil',                 # 7
    'FAMEmail',                 # 8
    'FAMDataAlta',              # 9
    'FAMIBAN',                  # 11 (saltamos FAMCCC que está en pos 10)
    'FAMBIC',                   # 12
    'bBaixa',                   # 14 (saltamos FAMNSocis en pos 13)
    'FAMObservacions',          # 15
    'FAMNIF',                   # 17 (saltamos FAMbSeccio en pos 16)
    'FAMDataNaixement',         # 18
    'FAMQuota',                 # 19
    'FAMDataBaixa',             # 21 (saltamos FAMIDSec en pos 20)
    'FAMSexe',                  # 23 (saltamos FAMTipus en pos 22)
    'FAMSociReferencia',        # 24
    'FAMbPagamentDomiciliat',   # 27 (saltamos FAMNewId y FAMNewIdRef)
    'FAMbRebutCobrat',          # 28
    'FAMPagamentFinestreta',    # 29
    'FAMTelefonEmergencia'      # 30
])

Dades = namedtuple('Dades', [
    'Presentador', 'CIFPresentador', 'Ordenant', 'CIFOrdenant',
    'IBANPresentador', 'BICPresentador', 'QuotaSocis',
    'SufixeRebuts', 'TexteRebutFinestreta'
])


class DatabaseModel:
    """
    Clase que gestiona la conexión a la base de datos y las operaciones CRUD.
    """
    def __init__(self):
        env_path = Path(__file__).resolve().parent / ".env"
        load_dotenv(dotenv_path=env_path)

        self.conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('SQL_SERVER')};"
            f"DATABASE={os.getenv('SQL_DATABASE')};"
            f"UID={os.getenv('SQL_USER')};"
            f"PWD={os.getenv('SQL_PASSWORD')};"
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
        query = """
            SELECT 
                FAMID,
                FAMNom,
                FAMAdressa,
                FAMPoblacio,
                FAMCodPos,
                FAMTelefon,
                FAMMobil,
                FAMEmail,
                FAMDataAlta,
                FAMIBAN,
                FAMBIC,
                bBaixa,
                FAMObservacions,
                FAMNIF,
                FAMDataNaixement,
                FAMQuota,
                FAMDataBaixa,
                FAMSexe,
                FAMSociReferencia,
                FAMbPagamentDomiciliat,
                FAMbRebutCobrat,
                FAMPagamentFinestreta,
                FAMTelefonEmergencia
            FROM scazorla_sa.G_Socis
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return [Socio(*row) for row in cursor.fetchall()]

    def famid_exists(self, famid: str) -> bool:
        famid = (famid or "").strip()
        if not famid:
            return False

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT 1 FROM scazorla_sa.G_Socis WHERE FAMID = ?",
            famid
        )
        return cursor.fetchone() is not None

    def get_dades(self):
        """Recupera los datos de configuración de la tabla G_Dades."""
        # Seleccionar explícitamente las columnas en el MISMO orden que Dades._fields
        columns = ", ".join(Dades._fields)
        query = f"SELECT {columns} FROM scazorla_sa.G_Dades WHERE RegID = 1"

        with self.conn.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
            if row:
                return Dades(*row)
            return None

    def socio_exists(self, fam_id):
        """Verifica si un socio con un FAMID específico ya existe."""
        query = "SELECT FAMID FROM scazorla_sa.G_Socis WHERE FAMID = ?"
        with self.conn.cursor() as cursor:
            cursor.execute(query, fam_id)
            return cursor.fetchone() is not None

    def add_socio(self, data):
        """Añade un nuevo socio a la base de datos."""
        # data ya viene con 22 campos desde el diálogo
        n_placeholders = len(data)  # ✅ Usar directamente len(data)
        placeholders = ', '.join(['?'] * n_placeholders)
        columns = ', '.join(Socio._fields)
        query = f"INSERT INTO scazorla_sa.G_Socis ({columns}) VALUES ({placeholders})"
    
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, data)  # ✅ Pasar data directamente
                self.conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al añadir socio: {ex}")
            return False

    def update_socio(self, data):
        """Actualiza un socio existente en la base de datos."""
        fam_id = data[0]

        # ============================================================================
        # LIMPIEZA Y VALIDACIÓN DE DATOS
        # ============================================================================
        data_clean = list(data)
    
        for i, (field_name, value) in enumerate(zip(Socio._fields, data)):
            # Campos numéricos: convertir strings vacíos a None
            if field_name == "FAMQuota":
                if value == "" or value is None:
                    data_clean[i] = None
                elif isinstance(value, str):
                    try:
                        data_clean[i] = float(value.replace(',', '.'))
                    except:
                        data_clean[i] = None
        
            # Campos de fecha: convertir strings a datetime
            elif field_name in ["FAMDataAlta", "FAMDataNaixement", "FAMDataBaixa"]:
                if value is None or value == "":
                    data_clean[i] = None
                elif isinstance(value, str):
                    try:
                        data_clean[i] = datetime.strptime(value.split()[0], '%Y-%m-%d')
                    except:
                        data_clean[i] = None
        
            # Campos booleanos: convertir strings a bool
            elif field_name in ["FAMbPagamentDomiciliat", "FAMbRebutCobrat", "FAMPagamentFinestreta", "bBaixa"]:
                if isinstance(value, str):
                    data_clean[i] = value.upper() in ['TRUE', '1', 'YES']
                elif value is None:
                    data_clean[i] = False
        
            # Strings vacíos a None
            elif isinstance(value, str) and value.strip() == "":
                data_clean[i] = None
    
        data = tuple(data_clean)
    
        # ============================================================================
        # DEBUG: Imprimir datos para diagnóstico
        # ============================================================================
        print("\n" + "="*80)
        print("DEBUG - DATOS A ACTUALIZAR:")
        print("="*80)
        for i, (field_name, value) in enumerate(zip(Socio._fields, data)):
            print(f"{i:2d}. {field_name:25s} = {value!r:40s} (tipo: {type(value).__name__})")
        print("="*80 + "\n")

        # Después de imprimir "DEBUG - DATOS LIMPIADOS:", añadir:
        print(f"\n🔍 DEBUG ESPECÍFICO NIF:")
        print(f"   Índice FAMNIF en Socio._fields: {Socio._fields.index('FAMNIF') if 'FAMNIF' in Socio._fields else 'NO ENCONTRADO'}")
        print(f"   Valor FAMNIF en data: '{data[13]}' (posición 13)")
        print(f"   Tipo: {type(data[13])}")
    
        # Excluir FAMID del SET ya que no se debe actualizar la clave primaria
        update_fields = [f for f in Socio._fields if f != 'FAMID']
        update_pairs = ', '.join([f"{col} = ?" for col in update_fields])
        query = f"UPDATE scazorla_sa.G_Socis SET {update_pairs} WHERE FAMID = ?"
    
        print(f"Query: {query}\n")
    
        try:
            with self.conn.cursor() as cursor:
                # Excluir el primer elemento (FAMID) de data y agregar FAMID al final para el WHERE
                ordered_data = data[1:] + (fam_id,)
            
                print("Datos ordenados para query:")
                for i, val in enumerate(ordered_data):
                    print(f"  ?{i+1} = {val!r} (tipo: {type(val).__name__})")
                print()
            
                cursor.execute(query, ordered_data)
                self.conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al actualizar socio: {ex}")
            return False
        
    def rename_socio(self, old_fam_id: str, new_fam_id: str) -> bool:
        """
        Renombra FAMID SIN duplicar filas. Actualiza referencias relacionadas.
        Todo en transacción.
        """
        old_fam_id = (old_fam_id or "").strip()
        new_fam_id = (new_fam_id or "").strip()

        if not old_fam_id or not new_fam_id:
            return False

        # Validaciones
        if not self.socio_exists(old_fam_id):
            print(f"Error: no existe el socio original {old_fam_id}")
            return False

        if old_fam_id == new_fam_id:
            return True

        if self.socio_exists(new_fam_id):
            print(f"Error: ya existe un socio con el nuevo ID {new_fam_id}")
            return False

        cursor = self.conn.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")

            # 1) Cambiar el ID en la tabla principal
            cursor.execute(
                "UPDATE scazorla_sa.G_Socis SET FAMID = ? WHERE FAMID = ?",
                new_fam_id, old_fam_id
            )
            if cursor.rowcount != 1:
                # Si no actualiza exactamente 1 fila, algo está mal (duplicados o no existe)
                cursor.execute("ROLLBACK")
                print(f"Error: se esperaban 1 fila actualizada y fueron {cursor.rowcount}")
                return False

            # 2) Actualizar referencias en la misma tabla (parejas)
            cursor.execute(
                "UPDATE scazorla_sa.G_Socis SET FAMSociReferencia = ? WHERE FAMSociReferencia = ?",
                new_fam_id, old_fam_id
            )

            # 3) Actualizar inscripciones de actividades
            cursor.execute(
                "UPDATE scazorla_sa.G_Activitats_Socis SET soci_codi = ? WHERE soci_codi = ?",
                new_fam_id, old_fam_id
            )

            cursor.execute("COMMIT")
            return True

        except Exception as ex:
            try:
                cursor.execute("ROLLBACK")
            except Exception:
                pass
            print(f"Error al renombrar socio: {ex}")
            return False
        finally:
            cursor.close()


    def delete_socio(self, fam_id):
        """Da de baja un socio (marca bBaixa = True y establece fecha de baja)."""
        from datetime import datetime
        query = "UPDATE scazorla_sa.G_Socis SET bBaixa = ?, FAMDataBaixa = ? WHERE FAMID = ?"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (True, datetime.now(), fam_id))
                self.conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al dar de baja socio: {ex}")
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

    def set_quota_for_all_socis(self, new_quota: float, only_active: bool = True) -> bool:
        """
        Replica la cuota (FAMQuota) a todos los socios.
        only_active=True -> solo socios NO baja (bBaixa = 0)
        """
        try:
            if new_quota is None:
                return False

            cursor = self.conn.cursor()
            try:
                cursor.execute("BEGIN TRANSACTION")

                if only_active:
                    cursor.execute(
                        "UPDATE scazorla_sa.G_Socis SET FAMQuota = ? WHERE ISNULL(bBaixa, 0) = 0",
                        new_quota
                    )
                else:
                    cursor.execute(
                        "UPDATE scazorla_sa.G_Socis SET FAMQuota = ?",
                        new_quota
                    )

                cursor.execute("COMMIT")
                return True

            except Exception:
                cursor.execute("ROLLBACK")
                raise
            finally:
                cursor.close()

        except pyodbc.Error as ex:
            print(f"Error al replicar quota a socios: {ex}")
            return False