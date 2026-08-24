using COJUB.Web.Models;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;

namespace COJUB.Web.Services;

public sealed class DocumentService
{
    private static readonly string Navy="#18352f";private static readonly string Coral="#df6549";

    public byte[] GeneralMembers(IReadOnlyList<Member> members,AppSettings settings,bool alphabetical)
    {
        var ordered=alphabetical?members.OrderBy(x=>x.Name).ThenBy(x=>x.Id):members.OrderBy(x=>NumericId(x.Id)).ThenBy(x=>x.Id);
        return QuestPDF.Fluent.Document.Create(doc=>doc.Page(page=>
        {
            Setup(page,"Llistat general de socis",settings.Presenter);
            page.Content().Table(table=>
            {
                table.ColumnsDefinition(c=>{c.ConstantColumn(42);c.RelativeColumn(2);c.RelativeColumn(2);c.RelativeColumn();c.RelativeColumn();});
                Header(table,"ID","Nom","Adreça","Població","Telèfon");
                foreach(var m in ordered)Row(table,m.Id,m.Name,m.Address??"",$"{m.PostalCode} {m.City}".Trim(),m.Mobile??m.Phone??"");
            });Footer(page);
        })).GeneratePdf();
    }

    public byte[] Banking(IReadOnlyList<Member> members,AppSettings settings)=>QuestPDF.Fluent.Document.Create(doc=>doc.Page(page=>
    {
        Setup(page,"Dades bancàries",settings.Presenter);page.Content().Table(table=>
        {
            table.ColumnsDefinition(c=>{c.ConstantColumn(42);c.RelativeColumn(2);c.RelativeColumn(2);c.RelativeColumn();c.ConstantColumn(55);});
            Header(table,"ID","Nom","IBAN","BIC","Quota");
            foreach(var m in members.OrderBy(x=>x.Name))Row(table,m.Id,m.Name,m.Iban??"",m.Bic??"",m.Fee?.ToString("0.00 €")??"");
        });Footer(page);
    })).GeneratePdf();

    public byte[] Labels(IReadOnlyList<Member> members)
    {
        var unique=members.Where(x=>!string.IsNullOrWhiteSpace(x.Address)).GroupBy(x=>$"{x.Address}|{x.PostalCode}|{x.City}".ToUpperInvariant()).Select(x=>x.First()).OrderBy(x=>x.Name).ToList();
        return QuestPDF.Fluent.Document.Create(doc=>doc.Page(page=>
        {
            page.Size(PageSizes.A4);page.MarginHorizontal(0);page.MarginVertical(4,Unit.Millimetre);
            page.Content().Column(column=>
            {
                for(var i=0;i<unique.Count;i+=3)
                {
                    var slice=unique.Skip(i).Take(3).ToList();column.Item().Height(37,Unit.Millimetre).Row(row=>
                    {
                        foreach(var member in slice)row.RelativeItem().PaddingHorizontal(5,Unit.Millimetre).PaddingVertical(4,Unit.Millimetre).BorderBottom(.3f).BorderColor(Colors.Grey.Lighten2).Column(c=>
                        {c.Item().Text(member.Name).SemiBold().FontSize(11);c.Item().Text(member.Address??"").FontSize(9);c.Item().Text($"{member.PostalCode} {member.City}".Trim()).FontSize(9);});
                        for(var j=slice.Count;j<3;j++)row.RelativeItem();
                    });
                }
            });
        })).GeneratePdf();
    }

    public byte[] ActivityReport(ActivityDetails details)=>QuestPDF.Fluent.Document.Create(doc=>doc.Page(page=>
    {
        Setup(page,details.Activity.Description,$"{details.Activity.StartDate:dd/MM/yyyy} · {details.Enrollments.Count} inscrits");
        page.Content().Table(table=>
        {
            table.ColumnsDefinition(c=>{c.ConstantColumn(75);c.RelativeColumn(2);c.RelativeColumn();c.ConstantColumn(65);c.ConstantColumn(50);});
            Header(table,"NIF","Nom","Tipus","Import","Pagat");
            foreach(var e in details.Enrollments)Row(table,e.Nif??"",e.MemberName,e.IsMember?"Soci":"No soci",$"{e.Amount:0.00} €",e.Paid?"Sí":"No");
        });Footer(page);
    })).GeneratePdf();

    private static void Setup(PageDescriptor page,string title,string? subtitle)
    {
        page.Size(PageSizes.A4);page.Margin(18,Unit.Millimetre);page.DefaultTextStyle(x=>x.FontFamily("Arial").FontSize(9).FontColor(Navy));
        page.Header().PaddingBottom(12).Row(row=>{row.RelativeItem().Column(c=>{c.Item().Text("COJUB").Bold().FontSize(20).FontColor(Coral);c.Item().Text(title).SemiBold().FontSize(14);if(!string.IsNullOrWhiteSpace(subtitle))c.Item().Text(subtitle).FontColor(Colors.Grey.Darken1);});row.ConstantItem(80).AlignRight().Text(DateTime.Now.ToString("dd/MM/yyyy")).FontSize(8);});
    }
    private static void Footer(PageDescriptor page)=>page.Footer().AlignCenter().Text(x=>{x.Span("COJUB · ");x.CurrentPageNumber();x.Span(" / ");x.TotalPages();});
    private static void Header(TableDescriptor t,params string[] values){foreach(var value in values)t.Cell().Background(Navy).Padding(5).Text(value).FontColor(Colors.White).SemiBold();}
    private static void Row(TableDescriptor t,params string[] values){foreach(var value in values)t.Cell().BorderBottom(.5f).BorderColor(Colors.Grey.Lighten2).Padding(5).Text(value);}
    private static int NumericId(string id)=>int.TryParse(id,out var parsed)?parsed:int.MaxValue;
}
