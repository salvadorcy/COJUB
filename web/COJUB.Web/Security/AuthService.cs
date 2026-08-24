using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using COJUB.Web.Data;
using COJUB.Web.Models;
using COJUB.Web.Services;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Identity;

namespace COJUB.Web.Security;

public sealed class AuthService(AuthRepository repository,IEmailSender emailSender,IConfiguration configuration)
{
    private readonly Models.AuthenticationOptions _options=configuration.GetSection("Authentication").Get<Models.AuthenticationOptions>()??new Models.AuthenticationOptions();
    private readonly PasswordHasher<WebUser> _passwordHasher=new();

    public async Task<Guid?> StartAsync(LoginInput input)
    {
        var user=await repository.FindUserAsync(input.Email);
        if(user is null||!user.IsActive)return null;
        var result=_passwordHasher.VerifyHashedPassword(user,user.PasswordHash,input.Password);
        if(result==PasswordVerificationResult.Failed)return null;
        var code=RandomNumberGenerator.GetInt32(0,1_000_000).ToString("D6");
        var id=Guid.NewGuid();
        var challenge=new LoginChallenge
        {
            Id=id,UserId=user.Id,CodeHash=Hash(id,code),ExpiresUtc=DateTime.UtcNow.AddMinutes(_options.OtpLifetimeMinutes),RememberMe=input.RememberMe
        };
        await repository.CreateChallengeAsync(challenge);
        await emailSender.SendOtpAsync(user.Email,user.DisplayName,code,_options.OtpLifetimeMinutes);
        return id;
    }

    public async Task<bool> CompleteAsync(HttpContext context,OtpInput input)
    {
        var challenge=await repository.GetChallengeAsync(input.ChallengeId);
        if(challenge is null||challenge.Used||challenge.ExpiresUtc<DateTime.UtcNow||challenge.Attempts>=_options.OtpMaxAttempts)return false;
        if(!CryptographicOperations.FixedTimeEquals(Convert.FromHexString(challenge.CodeHash),Convert.FromHexString(Hash(challenge.Id,input.Code))))
        {
            await repository.RegisterFailureAsync(challenge.Id);return false;
        }
        var user=await repository.GetUserAsync(challenge.UserId);
        if(user is null||!user.IsActive)return false;
        if (!await repository.ConsumeAsync(challenge.Id,user.Id)) return false;
        var claims=new[]
        {
            new Claim(ClaimTypes.NameIdentifier,user.Id.ToString()),new Claim(ClaimTypes.Email,user.Email),
            new Claim(ClaimTypes.Name,user.DisplayName),new Claim(ClaimTypes.Role,user.Role)
        };
        var identity=new ClaimsIdentity(claims,CookieAuthenticationDefaults.AuthenticationScheme);
        var properties=new AuthenticationProperties{IsPersistent=challenge.RememberMe,AllowRefresh=true};
        if(challenge.RememberMe)properties.ExpiresUtc=DateTimeOffset.UtcNow.AddDays(_options.RememberMeDays);
        await context.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme,new ClaimsPrincipal(identity),properties);
        return true;
    }

    private string Hash(Guid challengeId,string code)
    {
        if(string.IsNullOrWhiteSpace(_options.OtpPepper))throw new InvalidOperationException("Falta Authentication:OtpPepper.");
        var bytes=SHA256.HashData(Encoding.UTF8.GetBytes($"{challengeId:N}|{code}|{_options.OtpPepper}"));
        return Convert.ToHexString(bytes);
    }
}
