using System.ComponentModel.DataAnnotations;

namespace COJUB.Web.Models;

public sealed class LoginInput
{
    [Required, EmailAddress] public string Email { get; set; } = "";
    [Required, DataType(DataType.Password)] public string Password { get; set; } = "";
    public bool RememberMe { get; set; }
}

public sealed class OtpInput
{
    [Required] public Guid ChallengeId { get; set; }
    [Required, RegularExpression("^[0-9]{6}$")] public string Code { get; set; } = "";
}

public sealed class WebUser
{
    public int Id { get; init; }
    public string Email { get; init; } = "";
    public string PasswordHash { get; init; } = "";
    public string DisplayName { get; init; } = "";
    public bool IsActive { get; init; }
    public string Role { get; init; } = "User";
}

public sealed class UserAdminInput
{
    public int? Id { get; set; }
    [Required, EmailAddress, StringLength(320)] public string Email { get; set; } = "";
    [Required, StringLength(200)] public string DisplayName { get; set; } = "";
    [DataType(DataType.Password), StringLength(200, MinimumLength = 12)] public string? Password { get; set; }
}

public sealed class LoginChallenge
{
    public Guid Id { get; init; }
    public int UserId { get; init; }
    public string CodeHash { get; init; } = "";
    public DateTime ExpiresUtc { get; init; }
    public int Attempts { get; init; }
    public bool RememberMe { get; init; }
    public bool Used { get; init; }
}

public sealed class AuthenticationOptions
{
    public int OtpLifetimeMinutes { get; init; } = 10;
    public int OtpMaxAttempts { get; init; } = 5;
    public int RememberMeDays { get; init; } = 14;
    public string OtpPepper { get; init; } = "";
}

public sealed class SmtpOptions
{
    public string Host { get; init; } = "";
    public int Port { get; init; } = 587;
    public bool UseSsl { get; init; } = true;
    public string Username { get; init; } = "";
    public string Password { get; init; } = "";
    public string FromEmail { get; init; } = "";
    public string FromName { get; init; } = "COJUB";
}
