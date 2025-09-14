import os
from datetime import datetime

class ReportGenerator:
    """Clase para generar informes en formato de texto."""

    def __init__(self):
        self.base_dir = "." # Se puede cambiar a una ruta específica

    def generate_general_report(self, socis_list, socis_map):
        """
        Genera un listado general de socios con datos básicos.
        
        Args:
            socis_list (list): Lista de objetos Socio a incluir en el informe.
            socis_map (dict): Diccionario para buscar socios por su ID.
        """
        filename = os.path.join(self.base_dir, "llistat_general.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Llistat General de Socis - Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 100 + "\n\n")

            for socio in socis_list:
                socio_pareja_nom = socis_map.get(socio.FAMSociReferencia, None)
                socio_pareja_display = f"Soci Parella: {socio_pareja_nom}" if socio_pareja_nom else "Soci Parella: N/A"

                f.write(f"ID: {socio.FAMID}\n")
                f.write(f"Nom: {socio.FAMNom}\n")
                f.write(f"Adreça: {socio.FAMAdressa}\n")
                f.write(f"Població: {socio.FAMPoblacio} ({socio.FAMCodPos})\n")
                f.write(f"Telèfon: {socio.FAMTelefon} / Mòbil: {socio.FAMMobil}\n")
                f.write(f"Email: {socio.FAMEmail}\n")
                f.write(f"{socio_pareja_display}\n")
                f.write("-" * 20 + "\n\n")

    def generate_banking_report(self, socis_list):
        """
        Genera un listado de socios con sus datos bancarios.
        
        Args:
            socis_list (list): Lista de objetos Socio a incluir en el informe.
        """
        filename = os.path.join(self.base_dir, "llistat_bancari.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Llistat de Dades Bancàries - Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 100 + "\n\n")

            for socio in socis_list:
                f.write(f"Nom: {socio.FAMNom}\n")
                f.write(f"IBAN: {socio.FAMIBAN}\n")
                f.write(f"BIC: {socio.FAMBIC}\n")
                f.write("-" * 20 + "\n\n")
