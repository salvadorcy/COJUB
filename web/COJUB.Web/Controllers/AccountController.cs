using COJUB.Web.Models;
using COJUB.Web.Security;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;

namespace COJUB.Web.Controllers;

[Route("compte")]
public sealed class AccountController(AuthService authService):Controller
{
    [AllowAnonymous,HttpGet("inici-sessio")]public IActionResult Login()=>User.Identity?.IsAuthenticated==true?RedirectToAction("Index","Home"):View(new LoginInput());
    [AllowAnonymous,HttpPost("inici-sessio"),EnableRateLimiting(RateLimitPolicies.Login)]
    public async Task<IActionResult> Login(LoginInput input)
    {
        if(!ModelState.IsValid)return View(input);
        try{var id=await authService.StartAsync(input);if(id is null){ModelState.AddModelError("","El correu o la contrasenya no són correctes.");return View(input);}return RedirectToAction(nameof(Verify),new{id});}
        catch(InvalidOperationException){ModelState.AddModelError("","No s'ha pogut enviar el codi d'accés. Contacta amb l'administrador.");return View(input);}
    }
    [AllowAnonymous,HttpGet("verificar")]public IActionResult Verify(Guid id)=>View(new OtpInput{ChallengeId=id});
    [AllowAnonymous,HttpPost("verificar"),EnableRateLimiting(RateLimitPolicies.Otp)]
    public async Task<IActionResult> Verify(OtpInput input){if(!ModelState.IsValid)return View(input);if(!await authService.CompleteAsync(HttpContext,input)){ModelState.AddModelError("","El codi no és vàlid, ha caducat o s'han superat els intents.");return View(input);}return RedirectToAction("Index","Home");}
    [Authorize,HttpPost("tancar-sessio")]public async Task<IActionResult> Logout(){await HttpContext.SignOutAsync();return RedirectToAction(nameof(Login));}
    [AllowAnonymous,HttpGet("acces-denegat")]public IActionResult AccessDenied()=>View();
}

