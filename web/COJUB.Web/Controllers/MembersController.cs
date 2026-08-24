using COJUB.Web.Data;
using COJUB.Web.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace COJUB.Web.Controllers;

[Authorize,Route("socis")]
public sealed class MembersController(MemberRepository repository):Controller
{
    [HttpGet("")]public async Task<IActionResult> Index([FromQuery]MemberSearch search){ViewBag.Search=search;return View(await repository.SearchAsync(search));}
    [HttpGet("nou")]public async Task<IActionResult> Create()=>View("Edit",new Member{Id=await repository.NextIdAsync(),JoinedOn=DateTime.Today});
    [HttpPost("nou")]public async Task<IActionResult> Create(Member member){if(!ModelState.IsValid)return View("Edit",member);try{await repository.SaveAsync(member,null);TempData["Success"]="Soci afegit correctament.";return RedirectToAction(nameof(Index));}catch(Exception ex){ModelState.AddModelError("",Friendly(ex));return View("Edit",member);}}
    [HttpGet("{id}/editar")]public async Task<IActionResult> Edit(string id){var m=await repository.GetAsync(id);if(m is null)return NotFound();ViewBag.OriginalId=m.Id;return View(m);}
    [HttpPost("{id}/editar")]public async Task<IActionResult> Edit(string id,Member member){if(!ModelState.IsValid){ViewBag.OriginalId=id;return View(member);}try{await repository.SaveAsync(member,id);TempData["Success"]="Soci actualitzat correctament.";return RedirectToAction(nameof(Index));}catch(Exception ex){ModelState.AddModelError("",Friendly(ex));ViewBag.OriginalId=id;return View(member);}}
    [HttpPost("{id}/baixa")]public async Task<IActionResult> Deactivate(string id){await repository.DeactivateAsync(id);TempData["Success"]="Soci donat de baixa.";return RedirectToAction(nameof(Index));}
    private static string Friendly(Exception ex)=>ex.Message.Contains("UNIQUE",StringComparison.OrdinalIgnoreCase)||ex.Message.Contains("PRIMARY KEY",StringComparison.OrdinalIgnoreCase)?"Ja existeix un soci amb aquest ID.":"No s'han pogut desar les dades del soci.";
}

