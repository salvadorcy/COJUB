using System.Threading.RateLimiting;
using Microsoft.AspNetCore.RateLimiting;

namespace COJUB.Web.Security;

public static class RateLimitPolicies
{
    public const string Login = "login";
    public const string Otp = "otp";

    public static void Configure(RateLimiterOptions options)
    {
        options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
        options.AddFixedWindowLimiter(Login, limiter =>
        {
            limiter.Window = TimeSpan.FromMinutes(15);
            limiter.PermitLimit = 8;
            limiter.QueueLimit = 0;
        });
        options.AddFixedWindowLimiter(Otp, limiter =>
        {
            limiter.Window = TimeSpan.FromMinutes(10);
            limiter.PermitLimit = 10;
            limiter.QueueLimit = 0;
        });
    }
}

