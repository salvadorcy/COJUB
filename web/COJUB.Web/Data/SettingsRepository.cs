using COJUB.Web.Models;
using Microsoft.Data.SqlClient;

namespace COJUB.Web.Data;

public sealed class SettingsRepository(SqlConnectionFactory connections)
{
    public async Task<AppSettings> GetAsync()
    {
        await using var connection = await connections.OpenAsync();
        const string sql = """
            SELECT Presentador, CIFPresentador, Ordenant, CIFOrdenant,
                   IBANPresentador, BICPresentador, QuotaSocis,
                   SufixeRebuts, TexteRebutFinestreta
            FROM scazorla_sa.G_Dades WHERE RegID=1
            """;
        await using var command = new SqlCommand(sql, connection);
        await using var reader = await command.ExecuteReaderAsync();
        if (!await reader.ReadAsync()) return new AppSettings();
        return new AppSettings
        {
            Presenter = Text(reader, 0), PresenterTaxId = Text(reader, 1), Creditor = Text(reader, 2),
            CreditorTaxId = Text(reader, 3), PresenterIban = Text(reader, 4), PresenterBic = Text(reader, 5),
            MemberFee = reader.IsDBNull(6) ? null : reader.GetDecimal(6), ReceiptSuffix = Text(reader, 7),
            CounterReceiptText = Text(reader, 8)
        };
    }

    public async Task SaveAsync(AppSettings settings, bool updateActiveFees)
    {
        await using var connection = await connections.OpenAsync();
        await using var transaction = await connection.BeginTransactionAsync();
        const string sql = """
            UPDATE scazorla_sa.G_Dades SET Presentador=@Presenter,
                CIFPresentador=@PresenterTaxId, Ordenant=@Creditor,
                CIFOrdenant=@CreditorTaxId, IBANPresentador=@Iban,
                BICPresentador=@Bic, QuotaSocis=@Fee,
                SufixeRebuts=@Suffix, TexteRebutFinestreta=@ReceiptText
            WHERE RegID=1
            """;
        await using (var command = new SqlCommand(sql, connection, (SqlTransaction)transaction))
        {
            AddText(command, "@Presenter", settings.Presenter, 255); AddText(command, "@PresenterTaxId", settings.PresenterTaxId, 10);
            AddText(command, "@Creditor", settings.Creditor, 255); AddText(command, "@CreditorTaxId", settings.CreditorTaxId, 10);
            AddAnsiText(command, "@Iban", settings.PresenterIban?.Replace(" ", ""), 24); AddAnsiText(command, "@Bic", settings.PresenterBic, 20);
            var fee = command.Parameters.Add("@Fee", System.Data.SqlDbType.Decimal); fee.Precision = 4; fee.Scale = 2; fee.Value = settings.MemberFee ?? (object)DBNull.Value;
            AddAnsiText(command, "@Suffix", settings.ReceiptSuffix, 30);
            AddText(command, "@ReceiptText", settings.CounterReceiptText, 1024);
            await command.ExecuteNonQueryAsync();
        }
        if (updateActiveFees && settings.MemberFee.HasValue)
        {
            await using var feeCommand = new SqlCommand(
                "UPDATE scazorla_sa.G_Socis SET FAMQuota=@Fee WHERE ISNULL(bBaixa,0)=0",
                connection, (SqlTransaction)transaction);
            feeCommand.Parameters.AddWithValue("@Fee", settings.MemberFee.Value);
            await feeCommand.ExecuteNonQueryAsync();
        }
        await transaction.CommitAsync();
    }

    private static string? Text(SqlDataReader r, int i) => r.IsDBNull(i) ? null : r.GetValue(i).ToString()?.Trim();
    private static void AddText(SqlCommand command, string name, string? value, int size) =>
        command.Parameters.Add(name, System.Data.SqlDbType.NVarChar, size).Value = value ?? (object)DBNull.Value;
    private static void AddAnsiText(SqlCommand command, string name, string? value, int size) =>
        command.Parameters.Add(name, System.Data.SqlDbType.Char, size).Value = value ?? (object)DBNull.Value;
}
