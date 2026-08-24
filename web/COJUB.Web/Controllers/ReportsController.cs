using COJUB.Web.Data;
using COJUB.Web.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace COJUB.Web.Controllers;

[Authorize,Route("documents")]
public sealed class ReportsController(MemberRepository members,SettingsRepository settings,ActivityRepository activities,DocumentService documents,SepaService sepa):Controller
{
    [HttpGet("socis")]public async Task<IActionResult>Members(bool alphabetical=true)=>File(documents.GeneralMembers(await members.GetActiveAsync(),await settings.GetAsync(),alphabetical),"application/pdf","llistat-general.pdf");
    [HttpGet("bancari")]public async Task<IActionResult>Banking()=>File(documents.Banking(await members.GetActiveAsync(),await settings.GetAsync()),"application/pdf","llistat-bancari.pdf");
    [HttpGet("etiquetes")]public async Task<IActionResult>Labels()=>File(documents.Labels(await members.GetActiveAsync()),"application/pdf","etiquetes-socis.pdf");
    [HttpGet("activitat/{id:int}")]public async Task<IActionResult>Activity(int id){var d=await activities.GetDetailsAsync(id);return d is null?NotFound():File(documents.ActivityReport(d),"application/pdf",$"activitat-{id}.pdf");}
    [HttpPost("sepa")]public async Task<IActionResult>Sepa()=>File(sepa.Generate(await settings.GetAsync(),await members.GetActiveAsync(true)),"application/xml",$"remesa-sepa-{DateTime.Today:yyyyMMdd}.xml");
}
