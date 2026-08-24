using System.Net;
using System.Net.Mail;
using COJUB.Web.Models;

namespace COJUB.Web.Services;

public sealed class SmtpEmailSender(IConfiguration configuration) : IEmailSender
{
    public async Task SendOtpAsync(string recipient,string displayName,string code,int lifetimeMinutes)
    {
        var options=configuration.GetSection("Smtp").Get<SmtpOptions>()??new SmtpOptions();
        if(string.IsNullOrWhiteSpace(options.Host)||string.IsNullOrWhiteSpace(options.FromEmail))
            throw new InvalidOperationException("La configuració SMTP no està completa.");
        using var message=new MailMessage
        {
            From=new MailAddress(options.FromEmail,options.FromName),
            Subject="Codi d'accés COJUB",
            Body=$"Hola {displayName},\n\nEl teu codi d'accés és: {code}\n\nCaduca en {lifetimeMinutes} minuts. Si no l'has sol·licitat, ignora aquest missatge.",
            IsBodyHtml=false
        };
        message.To.Add(new MailAddress(recipient));
        using var client=new SmtpClient(options.Host,options.Port)
        {
            EnableSsl=options.UseSsl,
            DeliveryMethod=SmtpDeliveryMethod.Network,
            UseDefaultCredentials=false,
            Credentials=new NetworkCredential(options.Username,options.Password)
        };
        await client.SendMailAsync(message);
    }
}

