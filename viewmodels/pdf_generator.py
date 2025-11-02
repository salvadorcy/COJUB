from fpdf import FPDF
from datetime import datetime

class PdfGenerator(FPDF):
    """Clase para generar informes en formato PDF."""
    
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, self.report_title, 0, 1, 'C')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 5, f"Data de generació: {datetime.now().strftime('%d-%m-%Y')}", 0, 1, 'R')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Pàgina {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_body(self, text):
        self.set_font('Helvetica', '', 12)
        self.multi_cell(0, 5, text)
        self.ln()

    def generate_general_report(self, socis_list, socis_map, filepath):
        """
        Genera un listado general de socios con datos básicos en formato PDF.
        
        Args:
            socis_list (list): Lista de objetos Socio a incluir en el informe.
            socis_map (dict): Diccionario para buscar socios por su ID.
            filepath (str): Ruta completa donde se guardará el PDF.
        """
        self.report_title = "Llistat General de Socis"
        self.alias_nb_pages()
        self.add_page()
        
        for socio in socis_list:
            socio_pareja_nom = socis_map.get(socio.FAMSociReferencia, None)
            socio_pareja_display = f"Soci Parella: {socio_pareja_nom}" if socio_pareja_nom else "Soci Parella: N/A"

            self.set_font('Helvetica', 'B', 12)
            self.cell(0, 7, f"ID: {socio.FAMID} - {socio.FAMNom}", 0, 1)
            self.set_font('Helvetica', '', 10)
            self.cell(0, 5, f"Adreça: {socio.FAMAdressa}", 0, 1)
            self.cell(0, 5, f"Població: {socio.FAMPoblacio} ({socio.FAMCodPos})", 0, 1)
            self.cell(0, 5, f"Telèfon: {socio.FAMTelefon} / Mòbil: {socio.FAMMobil}", 0, 1)
            self.cell(0, 5, f"Email: {socio.FAMEmail}", 0, 1)
            self.cell(0, 5, f"{socio_pareja_display}", 0, 1)
            self.ln(5)
            
        self.output(filepath)

    def generate_banking_report(self, socis_list, filepath):
        """
        Genera un listado de socios con sus datos bancarios en formato PDF.
        
        Args:
            socis_list (list): Lista de objetos Socio a incluir en el informe.
            filepath (str): Ruta completa donde se guardará el PDF.
        """
        self.report_title = "Llistat de Dades Bancàries"
        self.alias_nb_pages()
        self.add_page()
        
        for socio in socis_list:
            self.set_font('Helvetica', 'B', 12)
            self.cell(0, 7, f"Nom: {socio.FAMNom}", 0, 1)
            self.set_font('Helvetica', '', 10)
            self.cell(0, 5, f"IBAN: {socio.FAMIBAN}", 0, 1)
            self.cell(0, 5, f"BIC: {socio.FAMBIC}", 0, 1)
            self.ln(5)
            
        self.output(filepath)