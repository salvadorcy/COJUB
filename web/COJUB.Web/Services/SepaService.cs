using System.Globalization;
using System.Text;
using System.Xml;
using COJUB.Web.Models;

namespace COJUB.Web.Services;

public sealed class SepaService
{
    public byte[] Generate(AppSettings settings,IReadOnlyList<Member> members)
    {
        if(members.Count==0)throw new InvalidOperationException("No hi ha socis per generar la remesa.");
        if(string.IsNullOrWhiteSpace(settings.Presenter)||string.IsNullOrWhiteSpace(settings.Creditor)||string.IsNullOrWhiteSpace(settings.PresenterIban)||string.IsNullOrWhiteSpace(settings.PresenterBic))
            throw new InvalidOperationException("Falten dades de configuració obligatòries per generar la remesa.");
        var invalid=members.Where(x=>!x.Fee.HasValue||x.Fee<=0||string.IsNullOrWhiteSpace(x.Iban)).Take(10).ToList();
        if(invalid.Count>0)throw new InvalidOperationException("Hi ha socis sense quota o IBAN vàlids: "+string.Join(", ",invalid.Select(x=>x.Id)));

        var now=DateTime.UtcNow;var messageId=$"COJUB-{now:yyyyMMddHHmmss}";var total=members.Sum(x=>x.Fee!.Value);
        var settingsXml=new XmlWriterSettings{Encoding=new UTF8Encoding(false),Indent=true};
        using var stream=new MemoryStream();using(var w=XmlWriter.Create(stream,settingsXml))
        {
            w.WriteStartDocument();w.WriteStartElement("Document","urn:iso:std:iso:20022:tech:xsd:pain.008.001.02");w.WriteStartElement("CstmrDrctDbtInitn");
            w.WriteStartElement("GrpHdr");Write(w,"MsgId",messageId);Write(w,"CreDtTm",now.ToString("yyyy-MM-ddTHH:mm:ss"));Write(w,"NbOfTxs",members.Count.ToString());Write(w,"CtrlSum",Money(total));
            w.WriteStartElement("InitgPty");Write(w,"Nm",settings.Presenter);w.WriteEndElement();w.WriteEndElement();
            w.WriteStartElement("PmtInf");Write(w,"PmtInfId",messageId+"-P1");Write(w,"PmtMtd","DD");Write(w,"BtchBookg","true");Write(w,"NbOfTxs",members.Count.ToString());Write(w,"CtrlSum",Money(total));
            w.WriteStartElement("PmtTpInf");w.WriteStartElement("SvcLvl");Write(w,"Cd","SEPA");w.WriteEndElement();w.WriteStartElement("LclInstrm");Write(w,"Cd","CORE");w.WriteEndElement();Write(w,"SeqTp","RCUR");w.WriteEndElement();
            Write(w,"ReqdColltnDt",DateTime.Today.AddDays(5).ToString("yyyy-MM-dd"));
            w.WriteStartElement("Cdtr");Write(w,"Nm",settings.Creditor);w.WriteEndElement();
            w.WriteStartElement("CdtrAcct");w.WriteStartElement("Id");Write(w,"IBAN",Clean(settings.PresenterIban));w.WriteEndElement();w.WriteEndElement();
            w.WriteStartElement("CdtrAgt");w.WriteStartElement("FinInstnId");Write(w,"BIC",Clean(settings.PresenterBic));w.WriteEndElement();w.WriteEndElement();Write(w,"ChrgBr","SLEV");
            w.WriteStartElement("CdtrSchmeId");w.WriteStartElement("Id");w.WriteStartElement("PrvtId");w.WriteStartElement("Othr");Write(w,"Id",settings.CreditorTaxId??settings.PresenterTaxId??"COJUB");w.WriteStartElement("SchmeNm");Write(w,"Prtry","SEPA");w.WriteEndElement();w.WriteEndElement();w.WriteEndElement();w.WriteEndElement();w.WriteEndElement();
            foreach(var m in members)
            {
                w.WriteStartElement("DrctDbtTxInf");w.WriteStartElement("PmtId");Write(w,"EndToEndId",$"COJUB-{Clean(m.Id)}-{now:yyyyMMdd}");w.WriteEndElement();
                w.WriteStartElement("InstdAmt");w.WriteAttributeString("Ccy","EUR");w.WriteString(Money(m.Fee!.Value));w.WriteEndElement();
                w.WriteStartElement("DrctDbtTx");w.WriteStartElement("MndtRltdInf");Write(w,"MndtId",$"MANDAT-{Clean(m.Id)}");Write(w,"DtOfSgntr",(m.JoinedOn??DateTime.Today).ToString("yyyy-MM-dd"));w.WriteEndElement();w.WriteEndElement();
                w.WriteStartElement("DbtrAgt");w.WriteStartElement("FinInstnId");if(!string.IsNullOrWhiteSpace(m.Bic))Write(w,"BIC",Clean(m.Bic));else{w.WriteStartElement("Othr");Write(w,"Id","NOTPROVIDED");w.WriteEndElement();}w.WriteEndElement();w.WriteEndElement();
                w.WriteStartElement("Dbtr");Write(w,"Nm",m.Name);w.WriteEndElement();w.WriteStartElement("DbtrAcct");w.WriteStartElement("Id");Write(w,"IBAN",Clean(m.Iban!));w.WriteEndElement();w.WriteEndElement();
                w.WriteStartElement("RmtInf");Write(w,"Ustrd",$"Quota soci {m.Id} {DateTime.Today:yyyy}");w.WriteEndElement();w.WriteEndElement();
            }
            w.WriteEndElement();w.WriteEndElement();w.WriteEndElement();w.WriteEndDocument();
        }
        return stream.ToArray();
    }
    private static void Write(XmlWriter w,string name,string value){w.WriteElementString(name,value);}
    private static string Clean(string value)=>value.Replace(" ","").Trim().ToUpperInvariant();
    private static string Money(decimal value)=>value.ToString("0.00",CultureInfo.InvariantCulture);
}

