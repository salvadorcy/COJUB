#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Backup de Socios antes de Sincronización

Este script crea una copia de seguridad de todos los socios en formato CSV
antes de ejecutar la sincronización desde Excel.

Autor: Sistema de Gestión COJUB
Fecha: 2024
"""

import os
import sys
import csv
from datetime import datetime
from dotenv import load_dotenv
import pyodbc

def crear_backup():
    """Crea un backup de todos los socios en formato CSV."""
    
    print("\n" + "="*70)
    print("💾 CREANDO BACKUP DE SOCIOS")
    print("="*70)
    
    # Cargar variables de entorno
    env_path = 'models/.env'
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        print(f"❌ Error: No se encuentra el archivo {env_path}")
        sys.exit(1)
    
    # Conectar a la base de datos
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('SQL_SERVER')};"
            f"DATABASE={os.getenv('SQL_DATABASE')};"
            f"UID={os.getenv('SQL_USER')};"
            f"PWD={os.getenv('SQL_PASSWORD')};"
        )
        conn = pyodbc.connect(conn_str)
        print("✅ Conexión a la base de datos establecida")
    except pyodbc.Error as ex:
        print(f"❌ Error al conectar a la base de datos: {ex}")
        sys.exit(1)
    
    # Crear carpeta de backups si no existe
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"📁 Carpeta '{backup_dir}' creada")
    
    # Nombre del archivo de backup con fecha y hora
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_socios_{timestamp}.csv")
    
    # Obtener todos los socios
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scazorla_sa.G_Socis")
        
        # Obtener nombres de columnas
        columns = [column[0] for column in cursor.description]
        
        # Escribir al CSV
        with open(backup_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(columns)  # Encabezados
            
            count = 0
            for row in cursor.fetchall():
                writer.writerow(row)
                count += 1
        
        print(f"✅ Backup creado exitosamente: {backup_file}")
        print(f"📊 Total de socios respaldados: {count}")
        print("="*70 + "\n")
        
        return backup_file
        
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    crear_backup()