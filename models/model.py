import pyodbc
from datetime import datetime
from dotenv import load_dotenv
import os

class Socio:
    """Clase para representar un socio."""
    def __init__(self, FAMID, FAMNom, FAMAdressa, FAMPoblacio, FAMCodPos, FAMTelefon, FAMMobil, FAMEmail,
                 FAMDataAlta, FAMCCC, FAMIBAN, FAMBIC, FAMNSocis, bBaixa, FAMObservacions,
                 FAMbSeccio, FAMNIF, FAMDataNaixement, FAMQuota, FAMIDSec, FAMDataBaixa,
                 FAMTipus, FAMSexe, FAMSociReferencia, FAMNewId, FAMNewIdRef, FAMbPagamentDomiciliat,
                 FAMbRebutCobrat, FAMPagamentFinestreta):
        self.FAMID = FAMID
        self.FAMNom = FAMNom
        self.FAMAdressa = FAMAdressa
        self.FAMPoblacio = FAMPoblacio
        self.FAMCodPos = FAMCodPos
        self.FAMTelefon = FAMTelefon
        self.FAMMobil = FAMMobil
        self.FAMEmail = FAMEmail
        self.FAMDataAlta = FAMDataAlta
        self.FAMCCC = FAMCCC
        self.FAMIBAN = FAMIBAN
        self.FAMBIC = FAMBIC
        self.FAMNSocis = FAMNSocis
        self.bBaixa = bBaixa
        self.FAMObservacions = FAMObservacions
        self.FAMbSeccio = FAMbSeccio
        self.FAMNIF = FAMNIF
        self.FAMDataNaixement = FAMDataNaixement
        self.FAMQuota = FAMQuota
        self.FAMIDSec = FAMIDSec
        self.FAMDataBaixa = FAMDataBaixa
        self.FAMTipus = FAMTipus
        self.FAMSexe = FAMSexe
        self.FAMSociReferencia = FAMSociReferencia
        self.FAMNewId = FAMNewId
        self.FAMNewIdRef = FAMNewIdRef
        self.FAMbPagamentDomiciliat = FAMbPagamentDomiciliat
        self.FAMbRebutCobrat = FAMbRebutCobrat
        self.FAMPagamentFinestreta = FAMPagamentFinestreta

class Dades:
    """Clase para representar los datos de configuración."""
    def __init__(self, TotalDefuncions, AcumulatDefuncions, PreuDerrama, ComissioBancaria, IdFactura,
                 Presentador, CIFPresentador, Ordenant, CIFOrdenant, IBANPresentador, BICPresentador,
                 RegID, PWD, QuotaSocis, SufixeRebuts, TexteRebutFinestreta):
        self.TotalDefuncions = TotalDefuncions
        self.AcumulatDefuncions = AcumulatDefuncions
        self.PreuDerrama = PreuDerrama
        self.ComissioBancaria = ComissioBancaria
        self.IdFactura = IdFactura
        self.Presentador = Presentador
        self.CIFPresentador = CIFPresentador
        self.Ordenant = Ordenant
        self.CIFOrdenant = CIFOrdenant
        self.IBANPresentador = IBANPresentador
        self.BICPresentador = BICPresentador
        self.RegID = RegID
        self.PWD = PWD
        self.QuotaSocis = QuotaSocis
        self.SufixeRebuts = SufixeRebuts
        self.TexteRebutFinestreta = TexteRebutFinestreta

class DatabaseModel:
    """Clase que maneja la conexión y operaciones de la base de datos."""
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        load_dotenv()
        """Establece la conexión a la base de datos SQL Server."""
        conn_str = (
           f"DRIVER={{ODBC Driver 17 for SQL Server}};"
           f"SERVER={os.getenv("SQL_SERVER")};"
           f"DATABASE={os.getenv("SQL_DATABASE")};"
           f"UID={os.getenv("SQL_USER")};"
           f"PWD={os.getenv("SQL_PASSWORD")};"
        )
        try:
            self.conn = pyodbc.connect(conn_str)
            self.cursor = self.conn.cursor()
            print("Conexión a la base de datos exitosa.")
        except Exception as e:
            print("Error al conectar a la base de datos:", e)

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()

    def get_all_socis(self):
        """Obtiene una lista de todos los socios."""
        if not self.cursor:
            return []
        self.cursor.execute("SELECT * FROM scazorla_sa.G_Socis")
        rows = self.cursor.fetchall()
        socis = []
        for row in rows:
            socis.append(Socio(*row))
        return socis

    def get_socio_by_id(self, famid):
        """Obtiene un socio por su FAMID."""
        if not self.cursor:
            return None
        self.cursor.execute("SELECT * FROM scazorla_sa.G_Socis WHERE FAMID = ?", famid)
        row = self.cursor.fetchone()
        return Socio(*row) if row else None

    def create_socio(self, socio_data):
        """Crea un nuevo socio en la base de datos."""
        if not self.cursor:
            return False
        try:
            query = """
            INSERT INTO scazorla_sa.G_Socis (FAMID, FAMNom, FAMAdressa, FAMPoblacio, FAMCodPos, FAMTelefon, FAMMobil,
            FAMEmail, FAMDataAlta, FAMCCC, FAMIBAN, FAMBIC, FAMNSocis, bBaixa, FAMObservacions,
            FAMbSeccio, FAMNIF, FAMDataNaixement, FAMQuota, FAMIDSec, FAMDataBaixa, FAMTipus,
            FAMSexe, FAMSociReferencia, FAMNewId, FAMNewIdRef, FAMbPagamentDomiciliat,
            FAMbRebutCobrat, FAMPagamentFinestreta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, *socio_data)
            self.conn.commit()
            return True
        except Exception as e:
            print("Error al crear socio:", e)
            self.conn.rollback()
            return False

    def update_socio(self, famid, socio_data):
        """Actualiza un socio existente en la base de datos."""
        if not self.cursor:
            return False
        try:
            query = """
            UPDATE scazorla_sa.G_Socis SET
            FAMNom=?, FAMAdressa=?, FAMPoblacio=?, FAMCodPos=?, FAMTelefon=?, FAMMobil=?, FAMEmail=?,
            FAMDataAlta=?, FAMCCC=?, FAMIBAN=?, FAMBIC=?, FAMNSocis=?, bBaixa=?, FAMObservacions=?,
            FAMbSeccio=?, FAMNIF=?, FAMDataNaixement=?, FAMQuota=?, FAMIDSec=?, FAMDataBaixa=?,
            FAMTipus=?, FAMSexe=?, FAMSociReferencia=?, FAMNewId=?, FAMNewIdRef=?, FAMbPagamentDomiciliat=?,
            FAMbRebutCobrat=?, FAMPagamentFinestreta=?
            WHERE FAMID=?
            """
            self.cursor.execute(query, *socio_data, famid)
            self.conn.commit()
            return True
        except Exception as e:
            print("Error al actualizar socio:", e)
            self.conn.rollback()
            return False

    def delete_socio(self, famid):
        """Elimina un socio de la base de datos."""
        if not self.cursor:
            return False
        try:
            self.cursor.execute("DELETE FROM scazorla_sa.G_Socis WHERE FAMID=?", famid)
            self.conn.commit()
            return True
        except Exception as e:
            print("Error al eliminar socio:", e)
            self.conn.rollback()
            return False

    def get_all_dades(self):
        """Obtiene los datos de configuración."""
        if not self.cursor:
            return None
        self.cursor.execute("SELECT * FROM scazorla_sa.G_Dades")
        row = self.cursor.fetchone()
        return Dades(*row) if row else None
    
    def update_dades(self, dades_data):
        """Actualiza los datos de configuración."""
        if not self.cursor:
            return False
        try:
            query = """
            UPDATE scazorla_sa.G_Dades SET
            TotalDefuncions=?, AcumulatDefuncions=?, PreuDerrama=?, ComissioBancaria=?,
            IdFactura=?, Presentador=?, CIFPresentador=?, Ordenant=?, CIFOrdenant=?,
            IBANPresentador=?, BICPresentador=?, PWD=?, QuotaSocis=?, SufixeRebuts=?,
            TexteRebutFinestreta=?
            WHERE RegID=1
            """
            self.cursor.execute(query, *dades_data)
            self.conn.commit()
            return True
        except Exception as e:
            print("Error al actualizar datos:", e)
            self.conn.rollback()
            return False
