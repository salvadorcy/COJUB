using COJUB.Web.Models;
using Microsoft.Data.SqlClient;

namespace COJUB.Web.Data;

public sealed class AuthRepository(SqlConnectionFactory connections)
{
    public async Task<WebUser?> FindUserAsync(string email)
    {
        await using var c=await connections.OpenAsync();
        const string sql="SELECT Id,Email,PasswordHash,DisplayName,IsActive,Role FROM scazorla_sa.COJUB_WebUsers WHERE NormalizedEmail=@Email";
        await using var cmd=new SqlCommand(sql,c); cmd.Parameters.AddWithValue("@Email",email.Trim().ToUpperInvariant());
        await using var r=await cmd.ExecuteReaderAsync();
        return await r.ReadAsync()?ReadUser(r):null;
    }

    public async Task CreateChallengeAsync(LoginChallenge challenge)
    {
        await using var c=await connections.OpenAsync();
        const string sql="""
            UPDATE scazorla_sa.COJUB_LoginChallenges SET Used=1 WHERE UserId=@UserId AND Used=0;
            INSERT INTO scazorla_sa.COJUB_LoginChallenges (Id,UserId,CodeHash,ExpiresUtc,Attempts,RememberMe,Used)
            VALUES (@Id,@UserId,@Hash,@Expires,0,@Remember,0)
            """;
        await using var cmd=new SqlCommand(sql,c);cmd.Parameters.AddWithValue("@Id",challenge.Id);cmd.Parameters.AddWithValue("@UserId",challenge.UserId);
        cmd.Parameters.AddWithValue("@Hash",challenge.CodeHash);cmd.Parameters.AddWithValue("@Expires",challenge.ExpiresUtc);cmd.Parameters.AddWithValue("@Remember",challenge.RememberMe);
        await cmd.ExecuteNonQueryAsync();
    }

    public async Task<LoginChallenge?> GetChallengeAsync(Guid id)
    {
        await using var c=await connections.OpenAsync();
        const string sql="SELECT Id,UserId,CodeHash,ExpiresUtc,Attempts,RememberMe,Used FROM scazorla_sa.COJUB_LoginChallenges WHERE Id=@Id";
        await using var cmd=new SqlCommand(sql,c);cmd.Parameters.AddWithValue("@Id",id);await using var r=await cmd.ExecuteReaderAsync();
        return await r.ReadAsync()?new LoginChallenge{Id=r.GetGuid(0),UserId=r.GetInt32(1),CodeHash=r.GetString(2),ExpiresUtc=r.GetDateTime(3),Attempts=r.GetInt32(4),RememberMe=r.GetBoolean(5),Used=r.GetBoolean(6)}:null;
    }

    public async Task<WebUser?> GetUserAsync(int id)
    {
        await using var c=await connections.OpenAsync();
        await using var cmd=new SqlCommand("SELECT Id,Email,PasswordHash,DisplayName,IsActive,Role FROM scazorla_sa.COJUB_WebUsers WHERE Id=@Id",c);cmd.Parameters.AddWithValue("@Id",id);
        await using var r=await cmd.ExecuteReaderAsync();return await r.ReadAsync()?ReadUser(r):null;
    }

    public async Task RegisterFailureAsync(Guid id)
    {
        await using var c=await connections.OpenAsync(); await using var cmd=new SqlCommand("UPDATE scazorla_sa.COJUB_LoginChallenges SET Attempts=Attempts+1 WHERE Id=@Id",c);cmd.Parameters.AddWithValue("@Id",id);await cmd.ExecuteNonQueryAsync();
    }

    public async Task<bool> ConsumeAsync(Guid id,int userId)
    {
        await using var c=await connections.OpenAsync();await using var tx=await c.BeginTransactionAsync();
        int consumed;
        await using(var cmd=new SqlCommand("UPDATE scazorla_sa.COJUB_LoginChallenges SET Used=1 WHERE Id=@Id AND Used=0 AND ExpiresUtc>SYSUTCDATETIME()",c,(SqlTransaction)tx)){cmd.Parameters.AddWithValue("@Id",id);consumed=await cmd.ExecuteNonQueryAsync();}
        if(consumed!=1){await tx.RollbackAsync();return false;}
        await using(var cmd=new SqlCommand("UPDATE scazorla_sa.COJUB_WebUsers SET LastLoginUtc=SYSUTCDATETIME() WHERE Id=@Id",c,(SqlTransaction)tx)){cmd.Parameters.AddWithValue("@Id",userId);await cmd.ExecuteNonQueryAsync();}
        await tx.CommitAsync();
        return true;
    }

    public async Task<IReadOnlyList<WebUser>> GetUsersAsync()
    {
        var result=new List<WebUser>();await using var c=await connections.OpenAsync();
        await using var cmd=new SqlCommand("SELECT Id,Email,PasswordHash,DisplayName,IsActive,Role FROM scazorla_sa.COJUB_WebUsers ORDER BY DisplayName,Email",c);
        await using var r=await cmd.ExecuteReaderAsync();while(await r.ReadAsync())result.Add(ReadUser(r));return result;
    }

    public async Task CreateUserAsync(UserAdminInput input,string passwordHash)
    {
        await using var c=await connections.OpenAsync();
        const string sql="INSERT INTO scazorla_sa.COJUB_WebUsers(Email,NormalizedEmail,PasswordHash,DisplayName,IsActive,Role) VALUES(@Email,@Normalized,@Hash,@Name,1,N'User')";
        await using var cmd=new SqlCommand(sql,c);AddText(cmd,"@Email",input.Email.Trim(),320);AddText(cmd,"@Normalized",input.Email.Trim().ToUpperInvariant(),320);AddText(cmd,"@Hash",passwordHash,1000);AddText(cmd,"@Name",input.DisplayName.Trim(),200);await cmd.ExecuteNonQueryAsync();
    }

    public async Task SetActiveAsync(int id,bool active,int administratorId)
    {
        await using var c=await connections.OpenAsync();await using var cmd=new SqlCommand("UPDATE scazorla_sa.COJUB_WebUsers SET IsActive=@Active WHERE Id=@Id AND Id<>@AdministratorId AND Role=N'User'",c);
        cmd.Parameters.AddWithValue("@Active",active);cmd.Parameters.AddWithValue("@Id",id);cmd.Parameters.AddWithValue("@AdministratorId",administratorId);await cmd.ExecuteNonQueryAsync();
    }

    public async Task SetPasswordAsync(int id,string passwordHash)
    {
        await using var c=await connections.OpenAsync();await using var cmd=new SqlCommand("UPDATE scazorla_sa.COJUB_WebUsers SET PasswordHash=@Hash WHERE Id=@Id",c);AddText(cmd,"@Hash",passwordHash,1000);cmd.Parameters.AddWithValue("@Id",id);await cmd.ExecuteNonQueryAsync();
    }

    private static WebUser ReadUser(SqlDataReader r)=>new(){Id=r.GetInt32(0),Email=r.GetString(1),PasswordHash=r.GetString(2),DisplayName=r.GetString(3),IsActive=r.GetBoolean(4),Role=r.GetString(5)};
    private static void AddText(SqlCommand command,string name,string value,int size)=>command.Parameters.Add(name,System.Data.SqlDbType.NVarChar,size).Value=value;
}
