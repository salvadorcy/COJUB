#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Completo: Backup + Sincronización de Socios

Este script:
1. Crea un backup automático de los socios actuales
2. Ejecuta la sincronización desde el Excel
3. Muestra un resumen completo

USO:
    python sincronizar_completo.py

Autor: Sistema de Gestión COJUB
Fecha: 2024
"""

import os
import sys
from datetime import datetime

def main():
    """Función principal que ejecuta backup y sincronización."""
    
    print("\n" + "="*70)
    print("🚀 SINCRONIZACIÓN COMPLETA DE SOCIOS")
    print("="*70)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*70 + "\n")
    
    # Verificar que existen los archivos necesarios
    if not os.path.exists("Socis-2025.xlsx"):
        print("❌ Error: No se encuentra el archivo Socis-2025.xlsx")
        print("   Coloca el archivo Excel en la carpeta del proyecto")
        sys.exit(1)
    
    if not os.path.exists("models/.env"):
        print("❌ Error: No se encuentra el archivo models/.env")
        print("   Crea el archivo .env con las credenciales de la base de datos")
        sys.exit(1)
    
    # Preguntar confirmación al usuario
    print("⚠️  ADVERTENCIA:")
    print("   Este script realizará los siguientes cambios en la base de datos:")
    print("   1. Actualizará los socios existentes con datos del Excel")
    print("   2. Insertará nuevos socios del Excel")
    print("   3. Marcará como BAJA los socios que NO estén en el Excel")
    print()
    
    respuesta = input("¿Deseas continuar? (escribe 'SI' para confirmar): ")
    
    if respuesta.upper() != 'SI':
        print("\n❌ Sincronización cancelada por el usuario")
        sys.exit(0)
    
    print("\n" + "="*70)
    print("PASO 1: CREANDO BACKUP DE SEGURIDAD")
    print("="*70 + "\n")
    
    # Importar y ejecutar backup
    try:
        from backup_socios import crear_backup
        backup_file = crear_backup()
        print(f"✅ Backup guardado en: {backup_file}\n")
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        print("   Se recomienda hacer un backup manual antes de continuar")
        respuesta = input("\n¿Deseas continuar sin backup? (escribe 'SI' para confirmar): ")
        if respuesta.upper() != 'SI':
            print("\n❌ Sincronización cancelada")
            sys.exit(0)
    
    print("\n" + "="*70)
    print("PASO 2: SINCRONIZANDO DESDE EXCEL")
    print("="*70 + "\n")
    
    # Importar y ejecutar sincronización
    try:
        from sincronizar_socios import SincronizadorSocios
        
        sincronizador = SincronizadorSocios("Socis-2025.xlsx", "models/.env")
        sincronizador.sincronizar()
        sincronizador.cerrar()
        
    except Exception as e:
        print(f"\n❌ Error durante la sincronización: {e}")
        print(f"   Puedes restaurar desde el backup: {backup_file if 'backup_file' in locals() else 'backups/'}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("="*70)
    print(f"📝 Backup disponible en: {backup_file if 'backup_file' in locals() else 'backups/'}")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)