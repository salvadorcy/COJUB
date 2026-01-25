from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Optional
from models.activitat import Activitat, ActivitatInscripcio
from database.db_manager import DatabaseManager
from datetime import date

class ActivitatViewModel(QObject):
    """ViewModel para la gestión de actividades"""
    
    activitats_updated = pyqtSignal()
    inscripcions_updated = pyqtSignal()
    error_occurred = pyqtSignal(str)
    success_message = pyqtSignal(str)
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self._activitats: List[Activitat] = []
        self._inscripcions: List[ActivitatInscripcio] = []
    
    # --- GESTIÓN DE ACTIVIDADES ---
    
    def load_activitats_actives(self):
        """Carga todas las actividades activas"""
        try:
            query = """
                SELECT id, descripcio, data_inici, data_fi, 
                       preu_soci, preu_no_soci, completada, activa,
                       created_at, updated_at
                FROM scazorla_sa.G_Activitats
                WHERE activa = 1
                ORDER BY data_inici DESC
            """
            rows = self.db_manager.execute_query(query)
            
            self._activitats = []
            for row in rows:
                activitat = Activitat(
                    id=row[0],
                    descripcio=row[1],
                    data_inici=row[2],
                    data_fi=row[3],
                    preu_soci=float(row[4]) if row[4] else 0.0,
                    preu_no_soci=float(row[5]) if row[5] else 0.0,
                    completada=bool(row[6]),
                    activa=bool(row[7]),
                    created_at=row[8],
                    updated_at=row[9]
                )
                self._activitats.append(activitat)
            
            self.activitats_updated.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Error carregant activitats: {str(e)}")
    
    def get_activitats(self) -> List[Activitat]:
        """Retorna la lista de actividades"""
        return self._activitats
    
    def create_activitat(self, activitat: Activitat) -> bool:
        """Crea una nova activitat"""
        try:
            query = """
                INSERT INTO scazorla_sa.G_Activitats 
                (descripcio, data_inici, data_fi, preu_soci, preu_no_soci, completada, activa)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """
            params = (
                activitat.descripcio,
                activitat.data_inici,
                activitat.data_fi,
                activitat.preu_soci,
                activitat.preu_no_soci,
                activitat.completada
            )
            
            self.db_manager.execute_non_query(query, params)
            self.success_message.emit("Activitat creada correctament")
            self.load_activitats_actives()
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error creant activitat: {str(e)}")
            return False
    
    def update_activitat(self, activitat: Activitat) -> bool:
        """Actualiza una activitat existent"""
        try:
            query = """
                UPDATE scazorla_sa.G_Activitats
                SET descripcio = ?, data_inici = ?, data_fi = ?, 
                    preu_soci = ?, preu_no_soci = ?, completada = ?,
                    updated_at = GETDATE()
                WHERE id = ?
            """
            params = (
                activitat.descripcio,
                activitat.data_inici,
                activitat.data_fi,
                activitat.preu_soci,
                activitat.preu_no_soci,
                activitat.completada,
                activitat.id
            )
            
            self.db_manager.execute_non_query(query, params)
            self.success_message.emit("Activitat actualitzada correctament")
            self.load_activitats_actives()
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error actualitzant activitat: {str(e)}")
            return False
    
    def delete_activitat(self, activitat_id: int) -> bool:
        """Marca una activitat com inactiva (borrado suave)"""
        try:
            query = """
                UPDATE scazorla_sa.G_Activitats
                SET activa = 0, updated_at = GETDATE()
                WHERE id = ?
            """
            self.db_manager.execute_non_query(query, (activitat_id,))
            self.success_message.emit("Activitat eliminada correctament")
            self.load_activitats_actives()
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error eliminant activitat: {str(e)}")
            return False
    
    # --- GESTIÓN DE INSCRIPCIONES ---
    
    def load_inscripcions(self, activitat_id: int):
        """Carga totes les inscripcions d'una activitat"""
        try:
            query = """
                SELECT 
                    i.id, i.activitat_id, i.soci_codi, i.data_inscripcio,
                    i.es_soci, i.pagat, i.import_pagat, i.observacions, i.activa,
                    s.Nom, s.Cognom1 + ' ' + ISNULL(s.Cognom2, '') as cognoms, s.NIF
                FROM scazorla_sa.G_Activitats_Socis i
                INNER JOIN scazorla_sa.G_Socis s ON i.soci_codi = s.FAMID
                WHERE i.activitat_id = ? AND i.activa = 1
                ORDER BY s.Cognom1, s.Cognom2, s.Nom
            """
            rows = self.db_manager.execute_query(query, (activitat_id,))
            
            self._inscripcions = []
            for row in rows:
                inscripcio = ActivitatInscripcio(
                    id=row[0],
                    activitat_id=row[1],
                    soci_codi=row[2],  # Ja es CHAR(5)
                    data_inscripcio=row[3],
                    es_soci=bool(row[4]),
                    pagat=bool(row[5]),
                    import_pagat=float(row[6]) if row[6] else None,
                    observacions=row[7] if row[7] else "",
                    activa=bool(row[8]),
                    nom_soci=row[9],
                    cognoms_soci=row[10],
                    nif_soci=row[11]
                )
                self._inscripcions.append(inscripcio)
            
            self.inscripcions_updated.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Error carregant inscripcions: {str(e)}")
    
    def get_inscripcions(self) -> List[ActivitatInscripcio]:
        """Retorna la lista de inscripciones"""
        return self._inscripcions
    
    def add_soci_to_activitat(self, activitat_id: int, soci_codi: str, 
                              es_soci: bool, preu: float) -> bool:
        """Inscribe un soci a una activitat"""
        try:
            # Verificar que no estigui ja inscrit
            check_query = """
                SELECT COUNT(*) FROM scazorla_sa.G_Activitats_Socis
                WHERE activitat_id = ? AND soci_codi = ? AND activa = 1
            """
            result = self.db_manager.execute_query(check_query, (activitat_id, soci_codi))
            
            if result and result[0][0] > 0:
                self.error_occurred.emit("Aquest soci ja està inscrit a l'activitat")
                return False
            
            query = """
                INSERT INTO scazorla_sa.G_Activitats_Socis
                (activitat_id, soci_codi, es_soci, import_pagat, pagat)
                VALUES (?, ?, ?, ?, 0)
            """
            params = (activitat_id, soci_codi, es_soci, preu)
            
            self.db_manager.execute_non_query(query, params)
            self.success_message.emit("Soci inscrit correctament")
            self.load_inscripcions(activitat_id)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error inscrivint soci: {str(e)}")
            return False
    
    def remove_soci_from_activitat(self, inscripcio_id: int, activitat_id: int) -> bool:
        """Da de baixa un soci d'una activitat (borrado suave)"""
        try:
            query = """
                UPDATE scazorla_sa.G_Activitats_Socis
                SET activa = 0
                WHERE id = ?
            """
            self.db_manager.execute_non_query(query, (inscripcio_id,))
            self.success_message.emit("Soci donat de baixa de l'activitat")
            self.load_inscripcions(activitat_id)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error donant de baixa soci: {str(e)}")
            return False
    
    def marcar_pagament(self, inscripcio_id: int, pagat: bool, activitat_id: int) -> bool:
        """Marca/desmarca el pagament d'una inscripció"""
        try:
            query = """
                UPDATE scazorla_sa.G_Activitats_Socis
                SET pagat = ?
                WHERE id = ?
            """
            self.db_manager.execute_non_query(query, (pagat, inscripcio_id))
            self.success_message.emit("Estat de pagament actualitzat")
            self.load_inscripcions(activitat_id)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error actualitzant pagament: {str(e)}")
            return False
    
    def get_estadistiques_activitat(self, activitat_id: int) -> dict:
        """Obtiene estadísticas d'una activitat"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_inscrits,
                    SUM(CASE WHEN pagat = 1 THEN 1 ELSE 0 END) as total_pagats,
                    SUM(CASE WHEN es_soci = 1 THEN 1 ELSE 0 END) as total_socis,
                    SUM(CASE WHEN pagat = 1 THEN import_pagat ELSE 0 END) as total_recaptat
                FROM scazorla_sa.G_Activitats_Socis
                WHERE activitat_id = ? AND activa = 1
            """
            result = self.db_manager.execute_query(query, (activitat_id,))
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    'total_inscrits': row[0] or 0,
                    'total_pagats': row[1] or 0,
                    'total_socis': row[2] or 0,
                    'total_recaptat': float(row[3]) if row[3] else 0.0
                }
            return {
                'total_inscrits': 0,
                'total_pagats': 0,
                'total_socis': 0,
                'total_recaptat': 0.0
            }
            
        except Exception as e:
            self.error_occurred.emit(f"Error obtenint estadístiques: {str(e)}")
            return {}