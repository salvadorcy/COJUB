from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom
import os

def generar_xml_sepa(dades, socios, filename="remesa_sepa.xml"):
    """
    Genera un archivo XML en formato SEPA (pain.008.001.02)
    para el cobro de la cuota de socios.
    """
    
    # 1. Crear el elemento raíz
    documento = Element("Document", xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02")
    cct_pago = SubElement(documento, "CstmrDrctDbtInitn")
    
    # 2. Encabezado del mensaje
    grupo_cabecera = SubElement(cct_pago, "GrpHdr")
    msg_id = SubElement(grupo_cabecera, "MsgId")
    msg_id.text = "MSGID-" + datetime.now().strftime("%Y%m%d%H%M%S")
    creacion_fecha = SubElement(grupo_cabecera, "CreDtTm")
    creacion_fecha.text = datetime.now().isoformat()
    num_transacciones = SubElement(grupo_cabecera, "NbOfTxs")
    num_transacciones.text = str(len(socios))
    
    total_control = sum(s.FAMQuota for s in socios)
    total_control_el = SubElement(grupo_cabecera, "CtrlSum")
    total_control_el.text = "{:.2f}".format(total_control)
    
    # Datos del presentador
    init_ptn = SubElement(grupo_cabecera, "InitgPty")
    nm = SubElement(init_ptn, "Nm")
    nm.text = dades.Presentador

    # 3. Información del pago
    pago_info = SubElement(cct_pago, "PmtInf")
    pago_id = SubElement(pago_info, "PmtInfId")
    pago_id.text = "PMTINFID-" + datetime.now().strftime("%Y%m%d%H%M%S")
    metodo_pago = SubElement(pago_info, "PmtMtd")
    metodo_pago.text = "DD"
    
    tipo_servicio = SubElement(pago_info, "PmtTpInf")
    cat_proposito = SubElement(tipo_servicio, "SvcLvl")
    code = SubElement(cat_proposito, "Cd")
    code.text = "SEPA"
    
    # Información del cobro
    tipo_cobro = SubElement(pago_info, "LclInstrm")
    proprty = SubElement(tipo_cobro, "Cd")
    proprty.text = "CORE"
    
    # 4. Información de la entidad deudora
    entidad_deudora = SubElement(pago_info, "Dbtr")
    nm_entidad = SubElement(entidad_deudora, "Nm")
    nm_entidad.text = dades.Ordenant
    
    dir_entidad = SubElement(entidad_deudora, "PstlAdr")
    dir_entidad.text = "Dirección del Ordenante" # TODO: Cambiar por un campo real
    
    # Cuenta del deudor
    cuenta_deudor = SubElement(pago_info, "DbtrAcct")
    id_cuenta = SubElement(cuenta_deudor, "Id")
    iban_cuenta = SubElement(id_cuenta, "IBAN")
    iban_cuenta.text = dades.IBANPresentador
    
    # Agente del deudor
    agente_deudor = SubElement(pago_info, "DbtrAgt")
    fin_inst_id = SubElement(agente_deudor, "FinInstnId")
    bic_agente = SubElement(fin_inst_id, "BIC")
    bic_agente.text = dades.BICPresentador
    
    # Esquema de domiciliación
    domiciliation = SubElement(pago_info, "DrctDbtPmtInf")
    sepa_id = SubElement(domiciliation, "DrctDbtId")
    sepa_id.text = "ES000000000000000000000" # TODO: Reemplazar con el ID de la domiciliación
    
    # 5. Información de las transacciones
    for socio in socios:
        creditor_trans = SubElement(pago_info, "DrctDbtTxInf")
        
        pago_id_trans = SubElement(creditor_trans, "PmtId")
        end_to_end_id = SubElement(pago_id_trans, "EndToEndId")
        end_to_end_id.text = socio.FAMID
        
        monto_trans = SubElement(creditor_trans, "InstdAmt", Ccy="EUR")
        monto_trans.text = "{:.2f}".format(socio.FAMQuota)

        deudor_trans = SubElement(creditor_trans, "Dbtr")
        nm_deudor = SubElement(deudor_trans, "Nm")
        nm_deudor.text = socio.FAMNom

        # Información de la cuenta del deudor
        cuenta_deudor_trans = SubElement(creditor_trans, "DbtrAcct")
        id_cuenta_deudor_trans = SubElement(cuenta_deudor_trans, "Id")
        iban_cuenta_deudor_trans = SubElement(id_cuenta_deudor_trans, "IBAN")
        iban_cuenta_deudor_trans.text = socio.FAMIBAN
        
        # Agente del deudor
        agente_deudor_trans = SubElement(creditor_trans, "DbtrAgt")
        fin_inst_id_trans = SubElement(agente_deudor_trans, "FinInstnId")
        bic_agente_trans = SubElement(fin_inst_id_trans, "BIC")
        bic_agente_trans.text = socio.FAMBIC
        
    # 6. Guardar el XML en un archivo
    arbol = ElementTree(documento)
    with open(filename, "w", encoding="utf-8") as f:
        # Embellecer y escribir el XML con sangría
        xml_str = tostring(documento, 'utf-8')
        dom = minidom.parseString(xml_str)
        f.write(dom.toprettyxml(indent="  "))
    
    print("Archivo SEPA generado en:", os.path.abspath(filename))