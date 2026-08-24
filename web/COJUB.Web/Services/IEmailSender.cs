namespace COJUB.Web.Services;

public interface IEmailSender
{
    Task SendOtpAsync(string recipient, string displayName, string code, int lifetimeMinutes);
}

