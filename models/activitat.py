from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class Activitat:
    """Modelo de datos para una actividad"""
    id: Optional[int] = None
    descripcio: str = ""
    data_inici: Optional[date] = None
    data_fi: Optional[date] = None
    preu_soci: float = 0.0
    preu_no_soci: float = 0.0
    completada: bool = False
    activa: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class ActivitatInscripcio:
    """Modelo para la inscripción de un socio en una actividad"""
    id: Optional[int] = None
    activitat_id: int = 0
    soci_codi: str = ""  # CAMBIADO: de int a str para FAMID (CHAR(5))
    data_inscripcio: Optional[datetime] = None
    es_soci: bool = True
    pagat: bool = False
    import_pagat: Optional[float] = None
    observacions: str = ""
    activa: bool = True
    
    # Campos adicionales para mostrar datos del socio
    nom_soci: str = ""
    cognoms_soci: str = ""
    nif_soci: str = ""