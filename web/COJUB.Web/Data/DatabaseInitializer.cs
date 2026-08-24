using Microsoft.AspNetCore.Identity;
using Microsoft.Data.SqlClient;

namespace COJUB.Web.Data;

public sealed class DatabaseInitializer(
    SqlConnectionFactory connections,
    IConfiguration configuration,
    ILogger<DatabaseInitializer> logger)
{
    public async Task InitializeAsync()
    {
        await using var connection = await connections.OpenAsync();
        var sql = """
            IF OBJECT_ID(N'scazorla_sa.COJUB_WebUsers', N'U') IS NULL
            BEGIN
                CREATE TABLE scazorla_sa.COJUB_WebUsers (
                    Id int IDENTITY(1,1) NOT NULL PRIMARY KEY,
                    Email nvarchar(320) NOT NULL,
                    NormalizedEmail nvarchar(320) NOT NULL,
                    PasswordHash nvarchar(1000) NOT NULL,
                    DisplayName nvarchar(200) NOT NULL,
                    Role nvarchar(30) NOT NULL CONSTRAINT DF_COJUB_WebUsers_Role DEFAULT N'User',
                    IsActive bit NOT NULL CONSTRAINT DF_COJUB_WebUsers_IsActive DEFAULT 1,
                    CreatedUtc datetime2 NOT NULL CONSTRAINT DF_COJUB_WebUsers_Created DEFAULT SYSUTCDATETIME(),
                    LastLoginUtc datetime2 NULL,
                    CONSTRAINT UQ_COJUB_WebUsers_Email UNIQUE (NormalizedEmail)
                );
            END;

            IF COL_LENGTH(N'scazorla_sa.COJUB_WebUsers', N'Role') IS NULL
                ALTER TABLE scazorla_sa.COJUB_WebUsers ADD Role nvarchar(30) NOT NULL
                    CONSTRAINT DF_COJUB_WebUsers_Role DEFAULT N'User';

            IF OBJECT_ID(N'scazorla_sa.COJUB_LoginChallenges', N'U') IS NULL
            BEGIN
                CREATE TABLE scazorla_sa.COJUB_LoginChallenges (
                    Id uniqueidentifier NOT NULL PRIMARY KEY,
                    UserId int NOT NULL,
                    CodeHash char(64) NOT NULL,
                    ExpiresUtc datetime2 NOT NULL,
                    Attempts int NOT NULL CONSTRAINT DF_COJUB_LoginChallenges_Attempts DEFAULT 0,
                    RememberMe bit NOT NULL,
                    Used bit NOT NULL CONSTRAINT DF_COJUB_LoginChallenges_Used DEFAULT 0,
                    CreatedUtc datetime2 NOT NULL CONSTRAINT DF_COJUB_LoginChallenges_Created DEFAULT SYSUTCDATETIME(),
                    CONSTRAINT FK_COJUB_LoginChallenges_User FOREIGN KEY (UserId)
                        REFERENCES scazorla_sa.COJUB_WebUsers(Id)
                );
                CREATE INDEX IX_COJUB_LoginChallenges_User_Expires
                    ON scazorla_sa.COJUB_LoginChallenges(UserId, ExpiresUtc DESC);
            END;

            DELETE FROM scazorla_sa.COJUB_LoginChallenges
            WHERE ExpiresUtc < DATEADD(day, -1, SYSUTCDATETIME()) OR Used = 1;
            """;
        await using (var command = new SqlCommand(sql, connection))
        {
            await command.ExecuteNonQueryAsync();
        }

        var email = configuration["BootstrapAdmin:Email"]?.Trim();
        var password = configuration["BootstrapAdmin:Password"];
        if (string.IsNullOrWhiteSpace(email) || string.IsNullOrWhiteSpace(password))
        {
            return;
        }

        const string findSql = "SELECT COUNT(*) FROM scazorla_sa.COJUB_WebUsers WHERE NormalizedEmail=@Email";
        await using var findCommand = new SqlCommand(findSql, connection);
        findCommand.Parameters.Add("@Email", System.Data.SqlDbType.NVarChar, 320).Value = email.ToUpperInvariant();
        var exists = Convert.ToInt32(await findCommand.ExecuteScalarAsync()) != 0;
        if (exists)
        {
            await using var roles = new SqlCommand("UPDATE scazorla_sa.COJUB_WebUsers SET Role=CASE WHEN NormalizedEmail=@Email THEN N'Administrator' ELSE N'User' END", connection);
            roles.Parameters.Add("@Email", System.Data.SqlDbType.NVarChar, 320).Value = email.ToUpperInvariant();
            await roles.ExecuteNonQueryAsync();
            return;
        }

        var user = new Models.WebUser { Email = email, DisplayName = "Administració COJUB" };
        var hash = new PasswordHasher<Models.WebUser>().HashPassword(user, password);
        const string insertSql = """
            INSERT INTO scazorla_sa.COJUB_WebUsers
                (Email, NormalizedEmail, PasswordHash, DisplayName, IsActive, Role)
            VALUES (@Email, @NormalizedEmail, @PasswordHash, @DisplayName, 1, N'Administrator');
            UPDATE scazorla_sa.COJUB_WebUsers SET Role=N'User' WHERE NormalizedEmail<>@NormalizedEmail;
            """;
        await using var insert = new SqlCommand(insertSql, connection);
        insert.Parameters.AddWithValue("@Email", email);
        insert.Parameters.AddWithValue("@NormalizedEmail", email.ToUpperInvariant());
        insert.Parameters.AddWithValue("@PasswordHash", hash);
        insert.Parameters.AddWithValue("@DisplayName", user.DisplayName);
        await insert.ExecuteNonQueryAsync();
        logger.LogInformation("S'ha creat l'usuari administrador inicial.");
    }
}
