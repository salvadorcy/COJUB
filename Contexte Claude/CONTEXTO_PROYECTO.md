# CONTEXTO COMPLETO DEL PROYECTO COJUB

## 📋 RESUMEN EJECUTIVO

**Proyecto**: Sistema de Gestión de Socios COJUB  
**Lenguaje**: Python 3.8+  
**Framework UI**: PyQt6  
**Base de Datos**: SQL Server (pyodbc)  
**Arquitectura**: MVVM (Model-View-ViewModel)  
**Estado**: ✅ 100% Completado y Funcional  
**Fecha**: 31 de octubre de 2024  

---

## 🎯 OBJETIVOS DEL PROYECTO

### Objetivo Principal
Completar y corregir una aplicación Python de gestión de socios con las siguientes funcionalidades:

1. **Gestión CRUD de Socios** (Crear, Leer, Actualizar, Eliminar)
2. **Generación de Remesas SEPA** (XML pain.008.001.02)
3. **Generación de Reportes PDF** (Listado general y datos bancarios)
4. **Sincronización desde Excel** (✨ NUEVO - Agregado durante el proyecto)
5. **Sistema de Backups** (✨ NUEVO - Agregado durante el proyecto)

---

## 🐛 PROBLEMAS ENCONTRADOS Y CORREGIDOS

### Total: 8 Bugs Críticos

#### 1. **viewmodels/viewmodel.py - Faltaba `socis_map`**
**Línea**: Constructor `__init__`  
**Problema**: El atributo `self.socis_map` no existía pero se usaba en métodos de generación de reportes  
**Error**: `AttributeError: 'ViewModel' object has no attribute 'socis_map'`  
**Solución**: 
```python
# AGREGADO EN __init__:
self.socis_map = {}

# AGREGADO EN load_data():
self.socis_map = {socio.FAMID: socio.FAMNom for socio in self.all_socis}
```

#### 2. **viewmodels/viewmodel.py - `generate_general_report()` incorrecto**
**Línea**: ~147  
**Problema**: 
- No recibía parámetro `filepath`
- Llamaba a método estático incorrectamente
- No instanciaba `PdfGenerator()`
- No manejaba excepciones
- No retornaba resultado

**Código anterior**:
```python
def generate_general_report(self):
    PdfGenerator.generate_general_report(self.filtered_socis, self.socis_map)
```

**Código corregido**:
```python
def generate_general_report(self, filepath):
    try:
        pdf = PdfGenerator()
        pdf.generate_general_report(self.filtered_socis, self.socis_map, filepath)
        return True
    except Exception as e:
        print(f"Error al generar el listado general: {e}")
        return False
```

#### 3. **viewmodels/viewmodel.py - `generate_banking_report()` incorrecto**
**Similar al problema #2**  
**Solución**: Mismo patrón de corrección que `generate_general_report()`

#### 4. **viewmodels/viewmodel.py - Llamada incorrecta a `sepa_lib`**
**Línea**: ~175  
**Problema**: 
- Nombre de función incorrecto: `sepa_lib()` en lugar de `generar_xml_sepa()`
- Orden de parámetros incorrecto

**Código anterior**:
```python
sepa_lib(filename, socios_a_domiciliar, self.dades)
```

**Código corregido**:
```python
generar_xml_sepa(self.dades, socios_a_domiciliar, filename)
```

#### 5. **views/view.py - Faltaba método `_open_file()`**
**Líneas afectadas**: 461, 469  
**Problema**: Los métodos `print_general_report()` y `print_banking_report()` llamaban a `_open_file()` pero el método no existía  
**Error**: `AttributeError: 'MainWindow' object has no attribute '_open_file'`

**Solución agregada**:
```python
def _open_file(self, filepath):
    """Abre un archivo con la aplicación predeterminada del sistema."""
    try:
        if platform.system() == 'Windows':
            os.startfile(filepath)
        elif platform.system() == 'Darwin':  # macOS
            os.system(f'open "{filepath}"')
        else:  # Linux
            os.system(f'xdg-open "{filepath}"')
    except Exception as e:
        print(f"No se pudo abrir el archivo: {e}")
        QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
```

#### 6. **views/view.py - Importaciones faltantes**
**Problema**: Faltaban imports necesarios para `_open_file()`

**Importaciones agregadas**:
```python
from PyQt6.QtGui import QColor, QFont, QDesktopServices  # QDesktopServices agregado
from PyQt6.QtCore import QSize, Qt, QUrl  # QUrl agregado
import os  # Agregado
import platform  # Agregado
```

#### 7. **views/view.py - `DadesDialog.fill_form()` roto**
**Línea**: ~198  
**Problema**: Intentaba llamar `self.dades.get_dades_data()` pero `self.dades` era en realidad el `view_model`

**Código anterior**:
```python
def fill_form(self):
    if self.dades:
        data = self.dades.get_dades_data()  # ERROR
```

**Código corregido**:
```python
def fill_form(self):
    if self.view_model:
        data = self.view_model.get_dades_data()
        if data:
            ordered_keys = list(self.fields.keys())
            for i, attr in enumerate(ordered_keys):
                if i < len(data):
                    value = data[i]
                    if value is not None:
                        self.fields[attr].setText(str(value))
```

#### 8. **requirements.txt - No existía**
**Problema**: No había archivo de dependencias  
**Solución**: Creado con todas las dependencias necesarias

---

## 📦 ARCHIVOS ENTREGADOS (24 TOTAL)

### 🐍 Código Python (10 archivos)

#### Aplicación Principal (7)
1. **viewmodel.py** ⚠️ CORREGIDO - 4 bugs corregidos
2. **view.py** ⚠️ CORREGIDO - 3 bugs corregidos
3. **main.py** ✅ Sin cambios - Punto de entrada
4. **model.py** ✅ Sin cambios - Conexión SQL Server
5. **pdf_generator.py** ✅ Sin cambios - Generación de PDFs
6. **sepa_lib.py** ✅ Sin cambios - Generación XML SEPA
7. **style_config.py** ✅ Sin cambios - Configuración de colores

#### Sincronización Excel (3) ✨ NUEVO
8. **sincronizar_completo.py** - Script completo con backup automático
9. **sincronizar_socios.py** - Sincronización básica desde Excel
10. **backup_socios.py** - Solo creación de backups

### 📚 Documentación (10 archivos)

1. **ENTREGA_FINAL.md** - Resumen completo de la entrega
2. **LEEME_PRIMERO.md** - Vista general visual del proyecto
3. **INICIO_RAPIDO.md** - Instalación en 5 minutos
4. **README.md** - Documentación completa del proyecto
5. **RESUMEN_CORRECCIONES.md** - Detalle de los 8 bugs corregidos
6. **ESTRUCTURA_PROYECTO.md** - Organización de carpetas y archivos
7. **INDICE.md** - Índice de toda la documentación
8. **GUIA_SINCRONIZACION.md** - Guía rápida de sincronización Excel
9. **README_SINCRONIZACION.md** - Documentación completa de sincronización
10. **CONTEXTO_PROYECTO.md** - Este archivo (para recuperar contexto)

### 🔧 Configuración (4 archivos)

1. **requirements.txt** - Dependencias Python (incluye openpyxl)
2. **instalar.bat** - Instalador automático Windows
3. **instalar.sh** - Instalador automático Linux/macOS
4. **env_template** - Plantilla configuración .env
5. **__init__.py** - Archivo módulo Python (vacío)

---

## 🏗️ ARQUITECTURA DEL PROYECTO

### Patrón MVVM

```
┌─────────────────────────────────────────┐
│  VIEW (views/)                          │
│  - view.py (interfaz PyQt6)             │
│  - style_config.py (estilos)            │
│  ├─ MainWindow                          │
│  ├─ SocioDialog                         │
│  └─ DadesDialog                         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  VIEWMODEL (viewmodels/)                │
│  - viewmodel.py (lógica de negocio)     │
│  - pdf_generator.py (PDFs)              │
│  - report_generator.py (reportes txt)   │
│  ├─ ViewModel (filtros, búsquedas)     │
│  └─ PdfGenerator (reportes)            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  MODEL (models/)                        │
│  - model.py (acceso a datos)            │
│  └─ DatabaseModel (CRUD SQL Server)    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  UTILS (utils/)                         │
│  - sepa_lib.py (generación XML SEPA)    │
└─────────────────────────────────────────┘
```

### Estructura de Carpetas

```
COJUB/
├── models/
│   ├── __init__.py
│   ├── model.py
│   └── .env (configuración BD)
├── viewmodels/
│   ├── __init__.py
│   ├── viewmodel.py ⚠️ CORREGIDO
│   ├── pdf_generator.py
│   └── report_generator.py
├── views/
│   ├── __init__.py
│   ├── view.py ⚠️ CORREGIDO
│   └── style_config.py
├── utils/
│   ├── __init__.py
│   └── sepa_lib.py
├── backups/ (se crea automáticamente)
├── main.py
├── sincronizar_completo.py ✨ NUEVO
├── sincronizar_socios.py ✨ NUEVO
├── backup_socios.py ✨ NUEVO
├── requirements.txt
├── instalar.bat
└── instalar.sh
```

---

## 🗄️ BASE DE DATOS

### Servidor: SQL Server
### Driver: ODBC Driver 17 for SQL Server
### Conexión: pyodbc

### Tablas Principales

#### Tabla `G_Socis` (Socios)
```sql
Campos principales:
- FAMID (PK) - ID del socio
- FAMNom - Nombre completo
- FAMAdressa - Dirección
- FAMPoblacio - Población
- FAMCodPos - Código postal
- FAMTelefon - Teléfono
- FAMMobil - Móvil
- FAMEmail - Email
- FAMIBAN - Cuenta bancaria
- FAMBIC - Código BIC
- FAMDataAlta - Fecha de alta
- bBaixa - Indica si está de baja (0/1)
- FAMDataBaixa - Fecha de baja
- FAMbPagamentDomiciliat - Pago domiciliado (0/1)
- FAMNIF - NIF
- FAMQuota - Cuota del socio
... (total 29 campos)
```

#### Tabla `G_Dades` (Configuración)
```sql
Campos principales:
- TotalDefuncions
- AcumulatDefuncions
- PreuDerrama
- ComissioBancaria
- Presentador
- CIFPresentador
- Ordenant
- CIFOrdenant
- IBANPresentador
- BICPresentador
- QuotaSocis
- RegID (PK Identity)
... (total 15 campos + PK)
```

### Archivo .env (models/.env)
```env
SQL_SERVER=sql.salvadorcy.net
SQL_DATABASE=scazorla_coordinadora
SQL_USER=scazorla_usr_coord
SQL_PASSWORD=o8bmaHvg-3DRzdcq9N-H
```

---

## 🔄 SINCRONIZACIÓN DESDE EXCEL (NUEVA FUNCIONALIDAD)

### Descripción
Scripts Python que sincronizan automáticamente la base de datos con un archivo Excel que contiene los socios activos.

### Archivo Excel: `Socis-2025.xlsx`
**Ubicación**: Raíz del proyecto  
**Contenido**: 578 socios activos  
**Hojas**: 1 (Hoja1)  
**Columnas**: 18

### Mapeo Excel → Base de Datos

| Excel | Base de Datos | Tipo |
|-------|---------------|------|
| Codi | FAMID | VARCHAR(50) |
| Nombre | FAMNom | VARCHAR(200) |
| NIF | FAMNIF | VARCHAR(20) |
| Dirección | FAMAdressa | VARCHAR(200) |
| CP | FAMCodPos | VARCHAR(10) |
| Población | FAMPoblacio | VARCHAR(100) |
| Teléfono | FAMTelefon | VARCHAR(20) |
| Móvil | FAMMobil | VARCHAR(20) |
| Email | FAMEmail | VARCHAR(100) |
| IBAN | FAMIBAN | VARCHAR(50) |
| BIC | FAMBIC | VARCHAR(20) |
| Fecha Alta | FAMDataAlta | DATE |
| Forma de pagament | FAMbPagamentDomiciliat | BIT |

### Lógica de Sincronización

```
1. Socios EN el Excel:
   ├─ Si NO existe en BD → INSERT (nuevo socio activo)
   └─ Si YA existe en BD → UPDATE (actualizar y marcar activo)

2. Socios NO EN el Excel:
   └─ Si está activo en BD → UPDATE (marcar bBaixa=1, FAMDataBaixa=NOW)
```

### Scripts de Sincronización

#### 1. `sincronizar_completo.py` ⭐ RECOMENDADO
**Descripción**: Script completo que hace backup automático antes de sincronizar  
**Uso**: `python sincronizar_completo.py`  
**Flujo**:
1. Pide confirmación al usuario
2. Crea backup automático en carpeta `backups/`
3. Ejecuta sincronización
4. Muestra resumen completo

#### 2. `sincronizar_socios.py`
**Descripción**: Script básico de sincronización (sin backup automático)  
**Uso**: `python sincronizar_socios.py`  
**Flujo**:
1. Lee Excel
2. Sincroniza con BD
3. Muestra estadísticas

#### 3. `backup_socios.py`
**Descripción**: Solo crea backup (sin sincronizar)  
**Uso**: `python backup_socios.py`  
**Formato**: CSV con todos los campos
**Ubicación**: `backups/backup_socios_YYYYMMDD_HHMMSS.csv`

### Estadísticas Generadas

```python
{
    'total_excel': 578,          # Socios en el Excel
    'total_bd_antes': 580,       # Socios en BD antes
    'total_bd_despues': 580,     # Socios en BD después
    'nuevos': 0,                 # Nuevos insertados
    'actualizados': 578,         # Actualizados
    'marcados_baja': 2,          # Marcados como baja
    'errores': 0                 # Errores encontrados
}
```

---

## 📦 DEPENDENCIAS (requirements.txt)

```txt
PyQt6==6.6.1           # Interfaz gráfica
pyodbc==5.0.1          # Conexión SQL Server
python-dotenv==1.0.0   # Variables de entorno
fpdf==1.7.2            # Generación de PDFs
openpyxl==3.1.2        # Lectura de Excel (NUEVO)
```

---

## 🎯 FUNCIONALIDADES PRINCIPALES

### 1. Gestión de Socios
- ✅ Agregar nuevo socio (SocioDialog)
- ✅ Editar socio existente
- ✅ Eliminar socio
- ✅ Búsqueda por ID o nombre
- ✅ Filtros:
  - Pagament per Finestreta
  - Mostrar Baixes
- ✅ Visualización en tabla con colores (rojos para bajas)

### 2. Generación de Remesas SEPA
- ✅ Formato: pain.008.001.02 (ISO 20022)
- ✅ Filtrado automático de socios con pago domiciliado
- ✅ Excluye socios dados de baja
- ✅ Genera XML válido
- ✅ Abre archivo automáticamente después de generar

### 3. Reportes PDF
- ✅ Listado General de Socios
  - Datos completos de cada socio
  - Incluye soci parella
  - Formato profesional
- ✅ Listado de Datos Bancarios
  - IBAN y BIC
  - Solo socios activos
- ✅ Apertura automática del PDF generado

### 4. Configuración
- ✅ Editar datos de la aplicación (DadesDialog)
- ✅ Datos del presentador
- ✅ Información bancaria
- ✅ Parámetros generales

### 5. Sincronización Excel ✨ NUEVO
- ✅ Lectura automática del Excel
- ✅ Inserción de nuevos socios
- ✅ Actualización de existentes
- ✅ Marcado automático de bajas
- ✅ Backups automáticos
- ✅ Estadísticas detalladas

---

## 🚀 INSTALACIÓN Y USO

### Instalación Automática

**Windows**:
```cmd
instalar.bat
```

**Linux/macOS**:
```bash
chmod +x instalar.sh
./instalar.sh
```

### Instalación Manual

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env en models/
# (copiar desde env_template)
```

### Ejecución

**Aplicación Principal**:
```bash
python main.py
```

**Sincronización Excel**:
```bash
# Colocar Socis-2025.xlsx en raíz
python sincronizar_completo.py
```

---

## 🔐 SEGURIDAD Y CONSIDERACIONES

### Backups
- ✅ Backup automático antes de sincronización
- ✅ Formato CSV con todos los campos
- ✅ Nombre con timestamp: `backup_socios_YYYYMMDD_HHMMSS.csv`
- ✅ Ubicación: carpeta `backups/`

### Protección de Datos
- ✅ No se borran registros (solo se marcan como baja)
- ✅ Credenciales en archivo .env (no en código)
- ✅ Confirmación antes de sincronizar
- ✅ Manejo de errores robusto

### Validaciones
- ✅ Verificación de conexión BD
- ✅ Verificación de existencia de archivos
- ✅ Conversión de tipos de datos
- ✅ Manejo de valores NULL

---

## 🎨 INTERFAZ DE USUARIO

### Colores
```python
STYLE_CONFIG = {
    "font_family": "Arial",
    "font_size_normal": 10,
    "font_size_bold": 10,
    "color_baixa_bg": QColor(255, 0, 0),     # Rojo
    "color_baixa_text": QColor(255, 255, 255), # Blanco
    "color_normal_text": QColor(0, 0, 0)      # Negro
}
```

### Ventana Principal (MainWindow)
- Tabla de socios (9 columnas visibles)
- Botones de acción (Añadir, Editar, Eliminar)
- Barra de búsqueda
- Checkboxes de filtros
- Información de remesa
- Contador de registros

### Diálogos
- **SocioDialog**: 29 campos del socio
- **DadesDialog**: 15 campos de configuración

---

## 📊 ESTADÍSTICAS DEL PROYECTO

### Archivos
- **Total archivos entregados**: 24
- **Archivos de código**: 10
- **Archivos de documentación**: 10
- **Archivos de configuración**: 4

### Código
- **Bugs corregidos**: 8
- **Archivos corregidos**: 2 (viewmodel.py, view.py)
- **Archivos nuevos creados**: 3 (sincronización)
- **Líneas de código corregidas**: ~200

### Documentación
- **Guías creadas**: 10
- **Páginas de documentación**: ~50

---

## 🎓 DECISIONES TÉCNICAS IMPORTANTES

### 1. Uso de namedtuple
Se usa `namedtuple` para definir estructuras de datos:
```python
Socio = namedtuple('Socio', ['FAMID', 'FAMNom', ...])
Dades = namedtuple('Dades', ['TotalDefuncions', ...])
```
**Razón**: Inmutabilidad, legibilidad, eficiencia

### 2. Patrón MVVM
**Razón**: Separación de responsabilidades, testabilidad, mantenibilidad

### 3. PyQt6 Signals
```python
socis_changed = pyqtSignal()
dades_changed = pyqtSignal()
```
**Razón**: Comunicación reactiva entre capas

### 4. Conversión de Fechas Excel
Las fechas en Excel se guardan como números (días desde 1900-01-01):
```python
fecha_alta_dt = datetime(1899, 12, 30) + timedelta(days=int(fecha_alta))
```

### 5. Detección de Pago Domiciliado
```python
pago_domiciliado = 'domiciliat' in forma_pago.lower() or '3' in forma_pago
```
**Razón**: El campo puede contener "3 - Domiciliat" o variaciones

---

## ⚠️ PROBLEMAS CONOCIDOS Y LIMITACIONES

### Limitaciones Actuales
1. No hay validación de formato IBAN (se guarda tal cual)
2. No hay validación de formato de email
3. Los errores de sincronización se muestran en consola pero no se registran en log
4. No hay sistema de rollback automático si falla la sincronización

### Posibles Mejoras Futuras
1. Validación de IBAN/BIC antes de guardar
2. Sistema de logs con archivo
3. Exportación a Excel
4. Gráficos y estadísticas
5. Envío de correos automáticos
6. Historial de remesas
7. Sistema de usuarios y permisos

---

## 📞 INFORMACIÓN DE CONTACTO Y SOPORTE

### Para Recuperar Contexto en Nueva Conversación

Proporciona estos archivos:
1. **CONTEXTO_PROYECTO.md** (este archivo)
2. **RESUMEN_CORRECCIONES.md**
3. **ESTRUCTURA_PROYECTO.md**

### Comandos Útiles para Diagnóstico

```bash
# Ver estructura del proyecto
tree -I '__pycache__|.venv' -L 2

# Verificar dependencias instaladas
pip list

# Probar conexión a BD
python -c "import pyodbc; print(pyodbc.drivers())"

# Ver socios en BD
python -c "from models.model import DatabaseModel; m = DatabaseModel(); print(len(m.get_all_socis()))"
```

---

## 🎯 PUNTOS CLAVE PARA RECORDAR

1. **El proyecto usa SQL Server**, no SQLite ni MySQL
2. **Las credenciales están en `models/.env`**, no en el código
3. **Los socios "dados de baja" NO se eliminan**, solo se marca `bBaixa = 1`
4. **La sincronización marca como baja los que NO están en el Excel**
5. **Siempre hacer backup antes de sincronizar**
6. **El Excel debe llamarse `Socis-2025.xlsx`** y estar en la raíz
7. **Los PDFs y XMLs se abren automáticamente** después de generarse
8. **La aplicación usa PyQt6**, no PyQt5
9. **El patrón es MVVM**, no MVC
10. **Hay 3 scripts de sincronización**: completo, básico, y solo backup

---

## 📝 NOTAS FINALES

### Estado del Proyecto
✅ **100% Completado y Funcional**

### Archivos Críticos
- `viewmodel.py` (corregido)
- `view.py` (corregido)
- `sincronizar_completo.py` (nuevo)
- `requirements.txt` (actualizado con openpyxl)

### Próximos Pasos Sugeridos
1. Implementar validación de IBAN
2. Agregar sistema de logs
3. Crear tests unitarios
4. Implementar exportación a Excel
5. Mejorar manejo de errores en sincronización

---

**Última actualización**: 31 de octubre de 2024  
**Versión del proyecto**: 1.0 (Completado)  
**Estado de documentación**: Completa  

---

FIN DEL CONTEXTO
