using System.ComponentModel.DataAnnotations;

namespace COJUB.Web.Models;

public sealed class Member
{
    [Required, StringLength(5)] public string Id { get; set; } = "";
    [Required, StringLength(255)] public string Name { get; set; } = "";
    [StringLength(255)] public string? Address { get; set; }
    [StringLength(255)] public string? City { get; set; }
    [StringLength(5)] public string? PostalCode { get; set; }
    [StringLength(20)] public string? Phone { get; set; }
    [StringLength(20)] public string? Mobile { get; set; }
    [EmailAddress, StringLength(100)] public string? Email { get; set; }
    public DateTime? JoinedOn { get; set; }
    [StringLength(24)] public string? Iban { get; set; }
    [StringLength(15)] public string? Bic { get; set; }
    public bool IsInactive { get; set; }
    [StringLength(2048)] public string? Notes { get; set; }
    [StringLength(10)] public string? Nif { get; set; }
    public DateTime? BirthDate { get; set; }
    [Range(0, 999999)] public decimal? Fee { get; set; }
    public DateTime? InactiveOn { get; set; }
    [StringLength(1)] public string? Sex { get; set; }
    [StringLength(255)] public string? PartnerMemberId { get; set; }
    public bool DirectDebit { get; set; }
    public bool ReceiptPaid { get; set; }
    public bool CounterPayment { get; set; }
    [StringLength(150)] public string? EmergencyPhone { get; set; }
}

public sealed class MemberListItem
{
    public string Id { get; init; } = "";
    public string Name { get; init; } = "";
    public string? Address { get; init; }
    public string? City { get; init; }
    public string? PostalCode { get; init; }
    public string? Phone { get; init; }
    public string? Mobile { get; init; }
    public string? Email { get; init; }
    public bool IsInactive { get; init; }
    public bool CounterPayment { get; init; }
    public string? PartnerName { get; init; }
}

public sealed class MemberSearch
{
    public string? Query { get; set; }
    public bool IncludeInactive { get; set; }
    public bool CounterPaymentOnly { get; set; }
}

public sealed class AppSettings
{
    [StringLength(255)] public string? Presenter { get; set; }
    [StringLength(10)] public string? PresenterTaxId { get; set; }
    [StringLength(255)] public string? Creditor { get; set; }
    [StringLength(10)] public string? CreditorTaxId { get; set; }
    [StringLength(24)] public string? PresenterIban { get; set; }
    [StringLength(20)] public string? PresenterBic { get; set; }
    [Range(0, 99.99)] public decimal? MemberFee { get; set; }
    [StringLength(30)] public string? ReceiptSuffix { get; set; }
    [StringLength(1024)] public string? CounterReceiptText { get; set; }
}

public sealed class Activity
{
    public int Id { get; set; }
    [Required, StringLength(200)] public string Description { get; set; } = "";
    [Required, DataType(DataType.Date)] public DateTime StartDate { get; set; } = DateTime.Today;
    [DataType(DataType.Date)] public DateTime? EndDate { get; set; }
    [Range(0, 9999.99)] public decimal MemberPrice { get; set; }
    [Range(0, 9999.99)] public decimal NonMemberPrice { get; set; }
    public bool Completed { get; set; }
    public bool Active { get; set; } = true;
}

public sealed class Enrollment
{
    public int Id { get; init; }
    public int ActivityId { get; init; }
    public string MemberId { get; init; } = "";
    public string MemberName { get; init; } = "";
    public string? Nif { get; init; }
    public bool IsMember { get; init; }
    public bool Paid { get; init; }
    public decimal Amount { get; init; }
    public string? Notes { get; init; }
}

public sealed class ActivityDetails
{
    public required Activity Activity { get; init; }
    public required IReadOnlyList<Enrollment> Enrollments { get; init; }
    public int PaidCount => Enrollments.Count(x => x.Paid);
    public decimal Collected => Enrollments.Where(x => x.Paid).Sum(x => x.Amount);
}

public sealed class EnrollmentInput
{
    [Required] public string MemberId { get; set; } = "";
    public bool IsMember { get; set; } = true;
    [Range(0, 9999.99)] public decimal Amount { get; set; }
}

