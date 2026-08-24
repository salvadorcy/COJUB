using System.Diagnostics;
using COJUB.Web.Data;
using Microsoft.AspNetCore.Mvc;
using COJUB.Web.Models;
using Microsoft.AspNetCore.Authorization;

namespace COJUB.Web.Controllers;

[Authorize]
public sealed class HomeController(MemberRepository members,ActivityRepository activities,SettingsRepository settings) : Controller
{
    public async Task<IActionResult> Index()
    {
        var active=await members.GetActiveAsync();var activityList=await activities.GetAllAsync();
        ViewBag.MemberCount=active.Count;ViewBag.DirectDebitCount=active.Count(x=>x.DirectDebit);
        ViewBag.CounterCount=active.Count(x=>x.CounterPayment);ViewBag.ActivityCount=activityList.Count;
        ViewBag.Settings=await settings.GetAsync();return View(activityList.Take(5));
    }

    [AllowAnonymous,ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = System.Diagnostics.Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}
