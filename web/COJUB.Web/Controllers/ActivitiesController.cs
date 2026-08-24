using COJUB.Web.Data;
using COJUB.Web.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace COJUB.Web.Controllers;

[Authorize,Route("activitats")]
public sealed class ActivitiesController(ActivityRepository activities,MemberRepository members):Controller
{
    [HttpGet("")]public async Task<IActionResult> Index()=>View(await activities.GetAllAsync());
    [HttpGet("nova")]public IActionResult Create()=>View("Edit",new Activity());
    [HttpPost("nova")]public async Task<IActionResult>Create(Activity activity){if(!ModelState.IsValid)return View("Edit",activity);await activities.SaveAsync(activity);return RedirectToAction(nameof(Index));}
    [HttpGet("{id:int}/editar")]public async Task<IActionResult>Edit(int id){var a=await activities.GetAsync(id);return a is null?NotFound():View(a);}
    [HttpPost("{id:int}/editar")]public async Task<IActionResult>Edit(int id,Activity activity){activity.Id=id;if(!ModelState.IsValid)return View(activity);await activities.SaveAsync(activity);return RedirectToAction(nameof(Index));}
    [HttpPost("{id:int}/baixa")]public async Task<IActionResult>Deactivate(int id){await activities.DeactivateAsync(id);return RedirectToAction(nameof(Index));}
    [HttpGet("{id:int}")]public async Task<IActionResult>Details(int id){var d=await activities.GetDetailsAsync(id);if(d is null)return NotFound();ViewBag.Members=await members.GetActiveAsync();return View(d);}
    [HttpPost("{id:int}/inscripcions")]public async Task<IActionResult>AddEnrollment(int id,EnrollmentInput input){if(ModelState.IsValid)await activities.AddEnrollmentAsync(id,input);return RedirectToAction(nameof(Details),new{id});}
    [HttpPost("{id:int}/inscripcions/{enrollmentId:int}/pagat")]public async Task<IActionResult>SetPaid(int id,int enrollmentId,bool paid){await activities.SetPaidAsync(enrollmentId,paid);return RedirectToAction(nameof(Details),new{id});}
    [HttpPost("{id:int}/inscripcions/{enrollmentId:int}/baixa")]public async Task<IActionResult>RemoveEnrollment(int id,int enrollmentId){await activities.RemoveEnrollmentAsync(enrollmentId);return RedirectToAction(nameof(Details),new{id});}
}

