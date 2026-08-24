using System.Security.Claims;
using COJUB.Web.Data;
using COJUB.Web.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;

namespace COJUB.Web.Controllers;

[Authorize(Roles = "Administrator"), Route("usuaris")]
public sealed class UsersController(AuthRepository repository) : Controller
{
    private readonly PasswordHasher<WebUser> _passwordHasher = new();

    [HttpGet("")] public async Task<IActionResult> Index() => View(await repository.GetUsersAsync());
    [HttpGet("nou")] public IActionResult Create() => View(new UserAdminInput());

    [HttpPost("nou")]
    public async Task<IActionResult> Create(UserAdminInput input)
    {
        if (string.IsNullOrWhiteSpace(input.Password)) ModelState.AddModelError(nameof(input.Password), "La contrasenya és obligatòria.");
        if (!ModelState.IsValid) return View(input);
        var user = new WebUser { Email = input.Email.Trim(), DisplayName = input.DisplayName.Trim() };
        try { await repository.CreateUserAsync(input, _passwordHasher.HashPassword(user, input.Password!)); }
        catch (SqlException exception) when (exception.Number is 2601 or 2627)
        {
            ModelState.AddModelError(nameof(input.Email), "Ja existeix un usuari amb aquest correu."); return View(input);
        }
        TempData["Success"] = "Usuari creat correctament."; return RedirectToAction(nameof(Index));
    }

    [HttpPost("{id:int}/estat")]
    public async Task<IActionResult> SetActive(int id, bool active)
    {
        await repository.SetActiveAsync(id, active, CurrentUserId());
        TempData["Success"] = active ? "Usuari activat." : "Usuari desactivat."; return RedirectToAction(nameof(Index));
    }

    [HttpPost("{id:int}/contrasenya")]
    public async Task<IActionResult> SetPassword(int id, string password)
    {
        if (string.IsNullOrWhiteSpace(password) || password.Length < 12)
        {
            TempData["Error"] = "La contrasenya ha de tenir almenys 12 caràcters."; return RedirectToAction(nameof(Index));
        }
        var user = await repository.GetUserAsync(id); if (user is null) return NotFound();
        await repository.SetPasswordAsync(id, _passwordHasher.HashPassword(user, password));
        TempData["Success"] = "Contrasenya actualitzada."; return RedirectToAction(nameof(Index));
    }

    private int CurrentUserId() => int.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)!);
}
