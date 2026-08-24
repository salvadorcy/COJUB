using COJUB.Web.Models;
using Microsoft.Data.SqlClient;

namespace COJUB.Web.Data;

public sealed class MemberRepository(SqlConnectionFactory connections)
{
    private const string MemberColumns = """
        s.FAMID, s.FAMNom, s.FAMAdressa, s.FAMPoblacio, s.FAMCodPos,
        s.FAMTelefon, s.FAMMobil, s.FAMEmail, s.FAMDataAlta, s.FAMIBAN,
        s.FAMBIC, s.bBaixa, s.FAMObservacions, s.FAMNIF, s.FAMDataNaixement,
        s.FAMQuota, s.FAMDataBaixa, s.FAMSexe, s.FAMSociReferencia,
        s.FAMbPagamentDomiciliat, s.FAMbRebutCobrat, s.FAMPagamentFinestreta,
        s.FAMTelefonEmergencia
        """;

    public async Task<IReadOnlyList<MemberListItem>> SearchAsync(MemberSearch search)
    {
        await using var connection = await connections.OpenAsync();
        var sql = """
            SELECT s.FAMID, s.FAMNom, s.FAMAdressa, s.FAMPoblacio, s.FAMCodPos,
                   s.FAMTelefon, s.FAMMobil, s.FAMEmail, ISNULL(s.bBaixa, 0),
                   ISNULL(s.FAMPagamentFinestreta, 0), partner.FAMNom
            FROM scazorla_sa.G_Socis s
            LEFT JOIN scazorla_sa.G_Socis partner
                ON LTRIM(RTRIM(partner.FAMID)) = LTRIM(RTRIM(s.FAMSociReferencia))
            WHERE (@IncludeInactive = 1 OR ISNULL(s.bBaixa, 0) = 0)
              AND (@CounterOnly = 0 OR ISNULL(s.FAMPagamentFinestreta, 0) = 1)
              AND (@Query = '' OR s.FAMID LIKE @LikeQuery OR s.FAMNom LIKE @LikeQuery
                   OR s.FAMNIF LIKE @LikeQuery OR s.FAMEmail LIKE @LikeQuery)
            ORDER BY s.FAMNom, s.FAMID
            """;
        await using var command = new SqlCommand(sql, connection);
        command.Parameters.AddWithValue("@IncludeInactive", search.IncludeInactive);
        command.Parameters.AddWithValue("@CounterOnly", search.CounterPaymentOnly);
        var query = search.Query?.Trim() ?? "";
        command.Parameters.AddWithValue("@Query", query);
        command.Parameters.AddWithValue("@LikeQuery", $"%{query}%");

        var result = new List<MemberListItem>();
        await using var reader = await command.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            result.Add(new MemberListItem
            {
                Id = Text(reader, 0), Name = Text(reader, 1), Address = NullableText(reader, 2),
                City = NullableText(reader, 3), PostalCode = NullableText(reader, 4),
                Phone = NullableText(reader, 5), Mobile = NullableText(reader, 6),
                Email = NullableText(reader, 7), IsInactive = reader.GetBoolean(8),
                CounterPayment = reader.GetBoolean(9), PartnerName = NullableText(reader, 10)
            });
        }
        return result;
    }

    public async Task<Member?> GetAsync(string id)
    {
        await using var connection = await connections.OpenAsync();
        var sql = $"SELECT {MemberColumns} FROM scazorla_sa.G_Socis s WHERE LTRIM(RTRIM(s.FAMID)) = @Id";
        await using var command = new SqlCommand(sql, connection);
        command.Parameters.AddWithValue("@Id", id.Trim());
        await using var reader = await command.ExecuteReaderAsync();
        return await reader.ReadAsync() ? MapMember(reader) : null;
    }

    public async Task<string> NextIdAsync()
    {
        await using var connection = await connections.OpenAsync();
        const string sql = """
            SELECT ISNULL(MAX(TRY_CONVERT(int, LTRIM(RTRIM(FAMID)))), 1000) + 1
            FROM scazorla_sa.G_Socis
            """;
        await using var command = new SqlCommand(sql, connection);
        return Convert.ToString(await command.ExecuteScalarAsync()) ?? "1001";
    }

    public async Task SaveAsync(Member member, string? originalId)
    {
        var id = member.Id.Trim().ToUpperInvariant();
        await using var connection = await connections.OpenAsync();
        await using var transaction = await connection.BeginTransactionAsync();
        try
        {
            if (string.IsNullOrWhiteSpace(originalId))
            {
                const string insert = """
                    INSERT INTO scazorla_sa.G_Socis
                    (FAMID, FAMNom, FAMAdressa, FAMPoblacio, FAMCodPos, FAMTelefon,
                     FAMMobil, FAMEmail, FAMDataAlta, FAMIBAN, FAMBIC, bBaixa,
                     FAMObservacions, FAMNIF, FAMDataNaixement, FAMQuota, FAMDataBaixa,
                     FAMSexe, FAMSociReferencia, FAMbPagamentDomiciliat,
                     FAMbRebutCobrat, FAMPagamentFinestreta, FAMTelefonEmergencia)
                    VALUES
                    (@Id, @Name, @Address, @City, @PostalCode, @Phone, @Mobile, @Email,
                     @JoinedOn, @Iban, @Bic, @Inactive, @Notes, @Nif, @BirthDate, @Fee,
                     @InactiveOn, @Sex, @PartnerId, @DirectDebit, @ReceiptPaid,
                     @CounterPayment, @EmergencyPhone)
                    """;
                await ExecuteMemberCommandAsync(connection, (SqlTransaction)transaction, insert, member, id);
            }
            else
            {
                var oldId = originalId.Trim();
                if (!string.Equals(oldId, id, StringComparison.OrdinalIgnoreCase))
                {
                    await ExecuteAsync(connection, (SqlTransaction)transaction,
                        "UPDATE scazorla_sa.G_Socis SET FAMID=@NewId WHERE FAMID=@OldId",
                        ("@NewId", id), ("@OldId", oldId));
                    await ExecuteAsync(connection, (SqlTransaction)transaction,
                        "UPDATE scazorla_sa.G_Socis SET FAMSociReferencia=@NewId WHERE FAMSociReferencia=@OldId",
                        ("@NewId", id), ("@OldId", oldId));
                    await ExecuteAsync(connection, (SqlTransaction)transaction,
                        "UPDATE scazorla_sa.G_Activitats_Socis SET soci_codi=@NewId WHERE soci_codi=@OldId",
                        ("@NewId", id), ("@OldId", oldId));
                }

                const string update = """
                    UPDATE scazorla_sa.G_Socis SET
                        FAMNom=@Name, FAMAdressa=@Address, FAMPoblacio=@City,
                        FAMCodPos=@PostalCode, FAMTelefon=@Phone, FAMMobil=@Mobile,
                        FAMEmail=@Email, FAMDataAlta=@JoinedOn, FAMIBAN=@Iban,
                        FAMBIC=@Bic, bBaixa=@Inactive, FAMObservacions=@Notes,
                        FAMNIF=@Nif, FAMDataNaixement=@BirthDate, FAMQuota=@Fee,
                        FAMDataBaixa=@InactiveOn, FAMSexe=@Sex,
                        FAMSociReferencia=@PartnerId,
                        FAMbPagamentDomiciliat=@DirectDebit,
                        FAMbRebutCobrat=@ReceiptPaid,
                        FAMPagamentFinestreta=@CounterPayment,
                        FAMTelefonEmergencia=@EmergencyPhone
                    WHERE LTRIM(RTRIM(FAMID))=@Id
                    """;
                await ExecuteMemberCommandAsync(connection, (SqlTransaction)transaction, update, member, id);
            }
            await transaction.CommitAsync();
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }

    public async Task DeactivateAsync(string id)
    {
        await using var connection = await connections.OpenAsync();
        const string sql = """
            UPDATE scazorla_sa.G_Socis
            SET bBaixa=1, FAMDataBaixa=GETDATE()
            WHERE LTRIM(RTRIM(FAMID))=@Id
            """;
        await using var command = new SqlCommand(sql, connection);
        command.Parameters.AddWithValue("@Id", id.Trim());
        await command.ExecuteNonQueryAsync();
    }

    public async Task<IReadOnlyList<Member>> GetActiveAsync(bool directDebitOnly = false)
    {
        await using var connection = await connections.OpenAsync();
        var sql = $"""
            SELECT {MemberColumns} FROM scazorla_sa.G_Socis s
            WHERE ISNULL(s.bBaixa,0)=0
              AND (@DirectDebitOnly=0 OR ISNULL(s.FAMbPagamentDomiciliat,0)=1)
            ORDER BY s.FAMNom, s.FAMID
            """;
        await using var command = new SqlCommand(sql, connection);
        command.Parameters.AddWithValue("@DirectDebitOnly", directDebitOnly);
        var result = new List<Member>();
        await using var reader = await command.ExecuteReaderAsync();
        while (await reader.ReadAsync()) result.Add(MapMember(reader));
        return result;
    }

    private static async Task ExecuteMemberCommandAsync(SqlConnection connection, SqlTransaction transaction,
        string sql, Member member, string id)
    {
        await using var command = new SqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("@Id", id);
        command.Parameters.AddWithValue("@Name", member.Name.Trim().ToUpperInvariant());
        Add(command, "@Address", member.Address?.Trim().ToUpperInvariant());
        Add(command, "@City", member.City?.Trim().ToUpperInvariant());
        Add(command, "@PostalCode", member.PostalCode?.Trim());
        Add(command, "@Phone", member.Phone?.Trim()); Add(command, "@Mobile", member.Mobile?.Trim());
        Add(command, "@Email", member.Email?.Trim().ToLowerInvariant()); Add(command, "@JoinedOn", member.JoinedOn);
        Add(command, "@Iban", member.Iban?.Replace(" ", "").ToUpperInvariant());
        Add(command, "@Bic", member.Bic?.Trim().ToUpperInvariant());
        command.Parameters.AddWithValue("@Inactive", member.IsInactive);
        Add(command, "@Notes", member.Notes?.Trim()); Add(command, "@Nif", member.Nif?.Trim().ToUpperInvariant());
        Add(command, "@BirthDate", member.BirthDate); Add(command, "@Fee", member.Fee);
        Add(command, "@InactiveOn", member.IsInactive ? member.InactiveOn ?? DateTime.Now : null);
        Add(command, "@Sex", member.Sex?.Trim().ToUpperInvariant());
        Add(command, "@PartnerId", member.PartnerMemberId?.Trim().ToUpperInvariant());
        command.Parameters.AddWithValue("@DirectDebit", member.DirectDebit);
        command.Parameters.AddWithValue("@ReceiptPaid", member.ReceiptPaid);
        command.Parameters.AddWithValue("@CounterPayment", member.CounterPayment);
        Add(command, "@EmergencyPhone", member.EmergencyPhone?.Trim());
        await command.ExecuteNonQueryAsync();
    }

    private static async Task ExecuteAsync(SqlConnection connection, SqlTransaction transaction, string sql,
        params (string Name, object Value)[] parameters)
    {
        await using var command = new SqlCommand(sql, connection, transaction);
        foreach (var parameter in parameters) command.Parameters.AddWithValue(parameter.Name, parameter.Value);
        await command.ExecuteNonQueryAsync();
    }

    private static void Add(SqlCommand command, string name, object? value) =>
        command.Parameters.AddWithValue(name, value ?? DBNull.Value);

    private static Member MapMember(SqlDataReader r) => new()
    {
        Id = Text(r, 0), Name = Text(r, 1), Address = NullableText(r, 2), City = NullableText(r, 3),
        PostalCode = NullableText(r, 4), Phone = NullableText(r, 5), Mobile = NullableText(r, 6),
        Email = NullableText(r, 7), JoinedOn = NullableDate(r, 8), Iban = NullableText(r, 9),
        Bic = NullableText(r, 10), IsInactive = !r.IsDBNull(11) && r.GetBoolean(11),
        Notes = NullableText(r, 12), Nif = NullableText(r, 13), BirthDate = NullableDate(r, 14),
        Fee = r.IsDBNull(15) ? null : r.GetDecimal(15), InactiveOn = NullableDate(r, 16),
        Sex = NullableText(r, 17), PartnerMemberId = NullableText(r, 18),
        DirectDebit = !r.IsDBNull(19) && r.GetBoolean(19),
        ReceiptPaid = !r.IsDBNull(20) && r.GetBoolean(20),
        CounterPayment = !r.IsDBNull(21) && r.GetBoolean(21), EmergencyPhone = NullableText(r, 22)
    };

    private static string Text(SqlDataReader r, int i) => r.IsDBNull(i) ? "" : r.GetValue(i).ToString()!.Trim();
    private static string? NullableText(SqlDataReader r, int i) => r.IsDBNull(i) ? null : r.GetValue(i).ToString()?.Trim();
    private static DateTime? NullableDate(SqlDataReader r, int i) => r.IsDBNull(i) ? null : r.GetDateTime(i);
}

