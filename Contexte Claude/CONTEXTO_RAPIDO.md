# CONTEXTO RÁPIDO - PROYECTO COJUB

## 🎯 QUÉ ES
Sistema de gestión de socios en Python con PyQt6 y SQL Server

## 📦 ENTREGADO
- **24 archivos** (10 código Python, 10 docs, 4 config)
- **8 bugs corregidos** en aplicación original
- **Sincronización Excel** (NUEVO - agregado)
- **Sistema de backups** (NUEVO - agregado)

## 🐛 BUGS CORREGIDOS
1. `viewmodel.py` - Faltaba `socis_map`
2. `viewmodel.py` - `generate_general_report()` incorrecto
3. `viewmodel.py` - `generate_banking_report()` incorrecto
4. `viewmodel.py` - Llamada incorrecta a `sepa_lib`
5. `view.py` - Faltaba método `_open_file()`
6. `view.py` - Importaciones faltantes
7. `view.py` - `DadesDialog.fill_form()` roto
8. `requirements.txt` - No existía

## 📂 ARCHIVOS CLAVE CORREGIDOS
- `viewmodels/viewmodel.py` ⚠️
- `views/view.py` ⚠️
- `requirements.txt` ✨ (incluye openpyxl)

## 🔄 SINCRONIZACIÓN EXCEL (NUEVO)
**Archivos**:
- `sincronizar_completo.py` ⭐ (con backup auto)
- `sincronizar_socios.py` (básico)
- `backup_socios.py` (solo backup)

**Funcionalidad**:
- Lee `Socis-2025.xlsx` (578 socios)
- Inserta nuevos socios
- Actualiza existentes
- **Marca como BAJA los que NO están en Excel**
- Crea backups en carpeta `backups/`

**Mapeo Excel → BD**:
- Codi → FAMID
- Nombre → FAMNom
- NIF → FAMNIF
- Dirección → FAMAdressa
- IBAN → FAMIBAN
- Forma de pagament → FAMbPagamentDomiciliat

## 🗄️ BASE DE DATOS
- **Servidor**: SQL Server
- **Driver**: ODBC Driver 17
- **Tablas**: G_Socis (29 campos), G_Dades (15 campos)
- **Conexión**: `models/.env`

```env
SQL_SERVER=sql.salvadorcy.net
SQL_DATABASE=scazorla_coordinadora
SQL_USER=scazorla_usr_coord
SQL_PASSWORD=o8bmaHvg-3DRzdcq9N-H
```

## 🏗️ ARQUITECTURA
**Patrón**: MVVM
```
views/ (view.py, style_config.py)
   ↓
viewmodels/ (viewmodel.py, pdf_generator.py)
   ↓
models/ (model.py)
```

## 📦 DEPENDENCIAS
```txt
PyQt6==6.6.1
pyodbc==5.0.1
python-dotenv==1.0.0
fpdf==1.7.2
openpyxl==3.1.2  # NUEVO - para Excel
```

## 🚀 USO RÁPIDO

**Aplicación**:
```bash
python main.py
```

**Sincronización**:
```bash
# Colocar Socis-2025.xlsx en raíz
python sincronizar_completo.py
```

## 📚 DOCUMENTACIÓN
1. **LEEME_PRIMERO.md** - Resumen visual
2. **INICIO_RAPIDO.md** - Instalación rápida
3. **GUIA_SINCRONIZACION.md** - Uso de sincronización
4. **RESUMEN_CORRECCIONES.md** - Bugs corregidos
5. **CONTEXTO_PROYECTO.md** - Contexto completo

## 🎯 FUNCIONALIDADES
- ✅ CRUD de socios
- ✅ Generación remesas SEPA
- ✅ Reportes PDF (general, bancario)
- ✅ Búsqueda y filtros
- ✅ Configuración
- ✅ Sincronización desde Excel (NUEVO)
- ✅ Backups automáticos (NUEVO)

## ⚠️ IMPORTANTE
- Los socios de baja NO se eliminan (solo `bBaixa=1`)
- La sincronización **marca como baja** los que NO están en Excel
- Siempre hacer backup antes de sincronizar
- El Excel debe estar en la raíz y llamarse `Socis-2025.xlsx`

## 🎓 PUNTOS CLAVE
1. SQL Server (no SQLite/MySQL)
2. PyQt6 (no PyQt5)
3. MVVM (no MVC)
4. Credenciales en `.env` (no en código)
5. namedtuple para estructuras de datos
6. Backups en CSV antes de sincronizar

## 📊 ESTADO
✅ **100% Completado y Funcional**

---

**Fecha**: 31 octubre 2024  
**Versión**: 1.0  
**Total archivos**: 24
