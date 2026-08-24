using COJUB.Web.Data;
using COJUB.Web.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace COJUB.Web.Controllers;

[Authorize,Route("configuracio")]
public sealed class SettingsController(SettingsRepository repository):Controller
{
    [HttpGet("")]public async Task<IActionResult> Index()=>View(await repository.GetAsync());
    [HttpPost("")]public async Task<IActionResult> Index(AppSettings settings,bool updateActiveFees){if(!ModelState.IsValid)return View(settings);await repository.SaveAsync(settings,updateActiveFees);TempData["Success"]="Configuració actualitzada.";return RedirectToAction(nameof(Index));}
}

