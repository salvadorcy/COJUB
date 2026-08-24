using Microsoft.Data.SqlClient;

namespace COJUB.Web.Data;

public sealed class SqlConnectionFactory(IConfiguration configuration)
{
    private readonly string _connectionString = configuration.GetConnectionString("COJUB")
        ?? throw new InvalidOperationException("Falta ConnectionStrings:COJUB.");

    public async Task<SqlConnection> OpenAsync(CancellationToken cancellationToken = default)
    {
        var connection = new SqlConnection(_connectionString);
        await connection.OpenAsync(cancellationToken);
        return connection;
    }
}

