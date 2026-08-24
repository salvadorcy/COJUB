using System.Globalization;
using COJUB.Web.Data;
using COJUB.Web.Security;
using COJUB.Web.Services;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.AspNetCore.HttpOverrides;
using QuestPDF.Infrastructure;

namespace COJUB.Web;

public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);

        var culture = CultureInfo.GetCultureInfo("ca-ES");
        CultureInfo.DefaultThreadCurrentCulture = culture;
        CultureInfo.DefaultThreadCurrentUICulture = culture;

        builder.Services.AddControllersWithViews(options =>
        {
            options.Filters.Add(new Microsoft.AspNetCore.Mvc.AutoValidateAntiforgeryTokenAttribute());
        });
        builder.Services.AddMemoryCache();
        builder.Services.AddHttpContextAccessor();
        builder.Services.AddRateLimiter(options => RateLimitPolicies.Configure(options));

        var keyDirectory = Path.GetFullPath(
            builder.Configuration["DataProtection:KeyDirectory"] ??
            Path.Combine(builder.Environment.ContentRootPath, "App_Data", "keys"));
        Directory.CreateDirectory(keyDirectory);
        builder.Services.AddDataProtection()
            .SetApplicationName("COJUB.Web")
            .PersistKeysToFileSystem(new DirectoryInfo(keyDirectory));

        builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
            .AddCookie(options =>
            {
                options.LoginPath = "/compte/inici-sessio";
                options.AccessDeniedPath = "/compte/acces-denegat";
                options.Cookie.Name = "__Host-COJUB.Auth";
                options.Cookie.HttpOnly = true;
                options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
                options.Cookie.SameSite = SameSiteMode.Strict;
                options.SlidingExpiration = true;
                options.ExpireTimeSpan = TimeSpan.FromHours(8);
            });
        builder.Services.AddAuthorization();

        builder.Services.AddSingleton<SqlConnectionFactory>();
        builder.Services.AddScoped<DatabaseInitializer>();
        builder.Services.AddScoped<MemberRepository>();
        builder.Services.AddScoped<SettingsRepository>();
        builder.Services.AddScoped<ActivityRepository>();
        builder.Services.AddScoped<AuthRepository>();
        builder.Services.AddScoped<AuthService>();
        builder.Services.AddScoped<IEmailSender, SmtpEmailSender>();
        builder.Services.AddScoped<DocumentService>();
        builder.Services.AddScoped<SepaService>();

        builder.Services.Configure<ForwardedHeadersOptions>(options =>
        {
            options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
            options.KnownIPNetworks.Clear();
            options.KnownProxies.Clear();
        });

        QuestPDF.Settings.License = LicenseType.Community;

        var app = builder.Build();

        app.UseForwardedHeaders();

        if (!app.Environment.IsDevelopment())
        {
            app.UseExceptionHandler("/Home/Error");
            app.UseHsts();
        }

        app.UseHttpsRedirection();
        app.Use(async (context, next) =>
        {
            context.Response.Headers.XContentTypeOptions = "nosniff";
            context.Response.Headers.XFrameOptions = "DENY";
            context.Response.Headers["Referrer-Policy"] = "strict-origin-when-cross-origin";
            context.Response.Headers.ContentSecurityPolicy =
                "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; " +
                "script-src 'self'; font-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'";
            context.Response.Headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()";
            await next();
        });
        app.UseRouting();
        app.UseRateLimiter();
        app.UseAuthentication();
        app.UseAuthorization();

        app.MapStaticAssets();
        app.MapControllerRoute(
            name: "default",
            pattern: "{controller=Home}/{action=Index}/{id?}")
            .WithStaticAssets();

        using (var scope = app.Services.CreateScope())
        {
            var initializer = scope.ServiceProvider.GetRequiredService<DatabaseInitializer>();
            initializer.InitializeAsync().GetAwaiter().GetResult();
        }

        app.Run();
    }
}
