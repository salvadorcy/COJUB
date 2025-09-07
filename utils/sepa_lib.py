import xml.etree.ElementTree as ET
import xml.dom.minidom

def calcular_iban_es(codigo_banco, codigo_agencia, dc, ccc):
    try:
        bban = f"{int(codigo_banco):04d}{int(codigo_agencia):04d}{int(dc):02d}{int(ccc):010d}"
        bban_con_es = bban + "142800"  # 'ES00' en números: E=14, S=28, 00
        mod_resultado = int(bban_con_es) % 97
        dc_iban = 98 - mod_resultado
        return f"ES{dc_iban:02d}{bban}"
    except:
        return ""

def generar_xml_sepa(df, presentador_nombre, presentador_cif, presentador_iban, presentador_sufijo, fecha_cargo, output_path="recibos_sepa.xml", incluir_instr_id=True, texto_remesa="Quota Aportacio Voluntaria 2025 - PART 1", fecha_firma="2008-07-01"):
    sepa_df = df.copy()
    if sepa_df.empty:
        return False

    ns = "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02"
    ET.register_namespace("", ns)

    root = ET.Element("Document", xmlns=ns)
    CstmrDrctDbtInitn = ET.SubElement(root, "CstmrDrctDbtInitn")

    GrpHdr = ET.SubElement(CstmrDrctDbtInitn, "GrpHdr")
    ET.SubElement(GrpHdr, "MsgId").text = "SEPA-MSG-001"
    ET.SubElement(GrpHdr, "CreDtTm").text = pd.Timestamp.now().isoformat()
    ET.SubElement(GrpHdr, "NbOfTxs").text = str(len(sepa_df))
    ET.SubElement(GrpHdr, "CtrlSum").text = f"{sepa_df['Quotes 2025'].sum() / 2:.2f}"

    InitgPty = ET.SubElement(GrpHdr, "InitgPty")
    ET.SubElement(InitgPty, "Nm").text = presentador_nombre

    PmtInf = ET.SubElement(CstmrDrctDbtInitn, "PmtInf")
    ET.SubElement(PmtInf, "PmtInfId").text = "REMESA-001"
    ET.SubElement(PmtInf, "PmtMtd").text = "DD"
    ET.SubElement(PmtInf, "BtchBookg").text = "true"
    ET.SubElement(PmtInf, "NbOfTxs").text = str(len(sepa_df))
    ET.SubElement(PmtInf, "CtrlSum").text = f"{sepa_df['Quotes 2025'].sum() / 2:.2f}"

    PmtTpInf = ET.SubElement(PmtInf, "PmtTpInf")
    SvcLvl = ET.SubElement(PmtTpInf, "SvcLvl")
    ET.SubElement(SvcLvl, "Cd").text = "SEPA"
    LclInstrm = ET.SubElement(PmtTpInf, "LclInstrm")
    ET.SubElement(LclInstrm, "Cd").text = "CORE"
    ET.SubElement(PmtTpInf, "SeqTp").text = "RCUR"
    ET.SubElement(PmtInf, "ReqdColltnDt").text = fecha_cargo

    Cdtr = ET.SubElement(PmtInf, "Cdtr")
    ET.SubElement(Cdtr, "Nm").text = presentador_nombre

    CdtrAcct = ET.SubElement(PmtInf, "CdtrAcct")
    Id = ET.SubElement(CdtrAcct, "Id")
    ET.SubElement(Id, "IBAN").text = presentador_iban

    CdtrAgt = ET.SubElement(PmtInf, "CdtrAgt")
    FinInstnId = ET.SubElement(CdtrAgt, "FinInstnId")
    ET.SubElement(FinInstnId, "BIC").text = "ESPBESMMXXX"

    CdtrSchmeId = ET.SubElement(PmtInf, "CdtrSchmeId")
    Id = ET.SubElement(CdtrSchmeId, "Id")
    PrvtId = ET.SubElement(Id, "PrvtId")
    Othr = ET.SubElement(PrvtId, "Othr")
    ET.SubElement(Othr, "Id").text = f"ES80{presentador_cif}{presentador_sufijo}"
    SchmeNm = ET.SubElement(Othr, "SchmeNm")
    ET.SubElement(SchmeNm, "Prtry").text = "SEPA"

    for i, row in sepa_df.iterrows():
        valor = float(row['Quotes 2025']) / 2
        if valor <= 0:
            continue

        # Obtener IBAN existente o calcularlo si falta
        iban = str(row.get("IBAN", "")).replace(" ", "")
        if not iban or iban.strip() == "nan":
            iban = calcular_iban_es(row["CodigoBanco"], row["CodigoAgencia"], row["DC"], row["CCC"])

        if not iban:
            continue  # saltar si no se puede obtener IBAN

        codigo_id = f"QV{i+1:03d}"
        DrctDbtTxInf = ET.SubElement(PmtInf, "DrctDbtTxInf")

        PmtId = ET.SubElement(DrctDbtTxInf, "PmtId")
        if incluir_instr_id:
            ET.SubElement(PmtId, "InstrId").text = codigo_id
        ET.SubElement(PmtId, "EndToEndId").text = codigo_id

        InstdAmt = ET.SubElement(DrctDbtTxInf, "InstdAmt", Ccy="EUR")
        InstdAmt.text = f"{valor:.2f}"

        DrctDbtTx = ET.SubElement(DrctDbtTxInf, "DrctDbtTx")
        MndtRltdInf = ET.SubElement(DrctDbtTx, "MndtRltdInf")
        ET.SubElement(MndtRltdInf, "MndtId").text = codigo_id
        ET.SubElement(MndtRltdInf, "DtOfSgntr").text = fecha_firma

        DbtrAgt = ET.SubElement(DrctDbtTxInf, "DbtrAgt")
        FinInstnId = ET.SubElement(DbtrAgt, "FinInstnId")
        ET.SubElement(FinInstnId, "BIC").text = ""

        Dbtr = ET.SubElement(DrctDbtTxInf, "Dbtr")
        ET.SubElement(Dbtr, "Nm").text = str(row.get("CompanyName", ""))

        DbtrAcct = ET.SubElement(DrctDbtTxInf, "DbtrAcct")
        Id = ET.SubElement(DbtrAcct, "Id")
        ET.SubElement(Id, "IBAN").text = iban

        RmtInf = ET.SubElement(DrctDbtTxInf, "RmtInf")
        ET.SubElement(RmtInf, "Ustrd").text = texto_remesa

    tree = ET.ElementTree(root)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    with open(output_path, "r", encoding="utf-8") as f:
        xml_string = f.read()
    parsed = xml.dom.minidom.parseString(xml_string)
    pretty_xml = parsed.toprettyxml(indent="  ")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    return True
