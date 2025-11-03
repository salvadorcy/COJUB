#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico - Campo FAMDataAlta
==========================================
Revisa por qué el campo de fecha de alta aparece en blanco.
"""

import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('models/.env')

# Intentar importar el modelo
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from models.model import DatabaseModel
    print("✓ Módulo DatabaseModel importado correctamente\n")
except Exception as e:
    print(f"✗ Error al importar DatabaseModel: {e}")
    print("Asegúrate de ejecutar este script desde la raíz del proyecto\n")
    sys.exit(1)

print("="*80)
print("DIAGNÓSTICO DEL CAMPO FAMDataAlta")
print("="*80)

try:
    # Conectar a BD
    print("\n1. Conectando a la base de datos...")
    model = DatabaseModel()
    print("   ✓ Conexión establecida\n")
    
    # Obtener todos los socios
    print("2. Obteniendo socios de la base de datos...")
    all_socis = model.get_all_socis()
    print(f"   ✓ Total de socios obtenidos: {len(all_socis)}\n")
    
    if len(all_socis) == 0:
        print("   ⚠ No hay socios en la base de datos")
        sys.exit(0)
    
    # Analizar el primer socio
    print("3. Analizando estructura del primer socio...")
    print("="*80)
    
    primer_socio = all_socis[0]
    print(f"   Tipo de objeto: {type(primer_socio)}")
    print(f"   Nombre del tipo: {primer_socio.__class__.__name__}\n")
    
    # Mostrar todos los campos
    print("4. Campos disponibles en el objeto socio:")
    print("-"*80)
    
    if hasattr(primer_socio, '_fields'):
        # Es un namedtuple
        print("   ✓ Es un namedtuple")
        print(f"   Campos (_fields): {primer_socio._fields}\n")
        
        for field in primer_socio._fields:
            valor = getattr(primer_socio, field, None)
            tipo = type(valor).__name__
            print(f"   • {field:25} = {valor!r:50} (tipo: {tipo})")
    else:
        # Es otro tipo de objeto
        print("   ℹ No es un namedtuple, listando atributos...")
        for attr in dir(primer_socio):
            if not attr.startswith('_'):
                valor = getattr(primer_socio, attr, None)
                if not callable(valor):
                    tipo = type(valor).__name__
                    print(f"   • {attr:25} = {valor!r:50} (tipo: {tipo})")
    
    print("\n" + "="*80)
    print("5. Análisis específico del campo de fecha:")
    print("-"*80)
    
    # Buscar campos relacionados con fecha de alta
    campos_fecha = []
    posibles_nombres = ['FAMDataAlta', 'dDataAlta', 'DataAlta', 'FechaAlta', 
                       'FAMFechaAlta', 'FAMDataAlta', 'fecha_alta']
    
    for nombre in posibles_nombres:
        if hasattr(primer_socio, nombre):
            valor = getattr(primer_socio, nombre)
            campos_fecha.append((nombre, valor))
            print(f"   ✓ ENCONTRADO: {nombre}")
            print(f"     Valor: {valor}")
            print(f"     Tipo: {type(valor)}")
            print(f"     Es None: {valor is None}")
            if valor is not None:
                print(f"     Representación: {repr(valor)}")
            print()
    
    if not campos_fecha:
        print("   ⚠ NO se encontró ningún campo de fecha de alta con nombres comunes")
        print("   Campos que contienen 'data' o 'fecha' en el nombre:")
        for attr in dir(primer_socio):
            if not attr.startswith('_'):
                if 'data' in attr.lower() or 'fecha' in attr.lower() or 'alta' in attr.lower():
                    valor = getattr(primer_socio, attr, None)
                    if not callable(valor):
                        print(f"     • {attr} = {valor!r}")
    
    # Analizar varios socios
    print("\n" + "="*80)
    print("6. Revisando primeros 5 socios:")
    print("-"*80)
    
    for i, socio in enumerate(all_socis[:5], 1):
        print(f"\n   Socio {i}:")
        print(f"   ID: {socio.FAMID}")
        print(f"   Nombre: {socio.FAMNom}")
        
        # Intentar acceder a FAMDataAlta
        if hasattr(socio, 'FAMDataAlta'):
            valor = socio.FAMDataAlta
            print(f"   FAMDataAlta: {valor} (tipo: {type(valor).__name__})")
            if valor is not None and hasattr(valor, 'strftime'):
                try:
                    print(f"   Formateado: {valor.strftime('%d/%m/%Y')}")
                except Exception as e:
                    print(f"   Error al formatear: {e}")
        else:
            print(f"   FAMDataAlta: NO EXISTE ESTE CAMPO")
    
    # Consulta SQL directa
    print("\n" + "="*80)
    print("7. Consultando directamente la tabla G_Socis:")
    print("-"*80)
    
    try:
        cursor = model.conn.cursor()
        
        # Ver estructura de la tabla
        cursor.execute("""
            SELECT TOP 1 * 
            FROM scazorla_sa.G_Socis
        """)
        
        columns = [column[0] for column in cursor.description]
        print(f"\n   Columnas en la tabla G_Socis:")
        for i, col in enumerate(columns, 1):
            print(f"   {i:2}. {col}")
        
        # Buscar columnas relacionadas con fecha
        print(f"\n   Columnas que contienen 'Data', 'Fecha' o 'Alta':")
        campos_fecha_db = [col for col in columns if 
                          'data' in col.lower() or 
                          'fecha' in col.lower() or 
                          'alta' in col.lower()]
        
        if campos_fecha_db:
            for col in campos_fecha_db:
                print(f"   ✓ {col}")
        else:
            print(f"   ⚠ No se encontraron columnas relacionadas")
        
        # Consultar valores reales
        print(f"\n   Valores de los primeros 5 registros:")
        cursor.execute("""
            SELECT TOP 5 FAMID, FAMNom, FAMDataAlta
            FROM scazorla_sa.G_Socis
        """)
        
        for row in cursor.fetchall():
            famid, famnom, data_alta = row
            print(f"   • ID {famid}: {famnom[:30]:30} → DataAlta: {data_alta}")
        
    except Exception as e:
        print(f"   ✗ Error en consulta SQL: {e}")
    
    print("\n" + "="*80)
    print("DIAGNÓSTICO COMPLETADO")
    print("="*80)
    
except Exception as e:
    print(f"\n✗ Error durante el diagnóstico: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    if 'model' in locals():
        model.close()
        print("\n✓ Conexión cerrada")