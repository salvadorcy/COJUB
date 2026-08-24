using COJUB.Web.Models;
using Microsoft.Data.SqlClient;

namespace COJUB.Web.Data;

public sealed class ActivityRepository(SqlConnectionFactory connections)
{
    public async Task<IReadOnlyList<Activity>> GetAllAsync()
    {
        await using var c = await connections.OpenAsync();
        const string sql = """
            SELECT id, descripcio, data_inici, data_fi, preu_soci, preu_no_soci, completada, activa
            FROM scazorla_sa.G_Activitats WHERE activa=1 ORDER BY data_inici DESC
            """;
        await using var cmd = new SqlCommand(sql, c);
        var result = new List<Activity>();
        await using var r = await cmd.ExecuteReaderAsync();
        while (await r.ReadAsync()) result.Add(Map(r));
        return result;
    }

    public async Task<Activity?> GetAsync(int id)
    {
        await using var c = await connections.OpenAsync();
        const string sql = """
            SELECT id, descripcio, data_inici, data_fi, preu_soci, preu_no_soci, completada, activa
            FROM scazorla_sa.G_Activitats WHERE id=@Id AND activa=1
            """;
        await using var cmd = new SqlCommand(sql, c); cmd.Parameters.AddWithValue("@Id", id);
        await using var r = await cmd.ExecuteReaderAsync(); return await r.ReadAsync() ? Map(r) : null;
    }

    public async Task SaveAsync(Activity activity)
    {
        await using var c = await connections.OpenAsync();
        var sql = activity.Id == 0
            ? "INSERT INTO scazorla_sa.G_Activitats (descripcio,data_inici,data_fi,preu_soci,preu_no_soci,completada,activa) VALUES (@Description,@Start,@End,@MemberPrice,@NonMemberPrice,@Completed,1)"
            : "UPDATE scazorla_sa.G_Activitats SET descripcio=@Description,data_inici=@Start,data_fi=@End,preu_soci=@MemberPrice,preu_no_soci=@NonMemberPrice,completada=@Completed,updated_at=GETDATE() WHERE id=@Id";
        await using var cmd = new SqlCommand(sql, c);
        cmd.Parameters.AddWithValue("@Id", activity.Id); cmd.Parameters.AddWithValue("@Description", activity.Description.Trim());
        cmd.Parameters.AddWithValue("@Start", activity.StartDate); cmd.Parameters.AddWithValue("@End", activity.EndDate ?? (object)DBNull.Value);
        cmd.Parameters.AddWithValue("@MemberPrice", activity.MemberPrice); cmd.Parameters.AddWithValue("@NonMemberPrice", activity.NonMemberPrice);
        cmd.Parameters.AddWithValue("@Completed", activity.Completed); await cmd.ExecuteNonQueryAsync();
    }

    public async Task DeactivateAsync(int id)
    {
        await using var c = await connections.OpenAsync();
        await using var cmd = new SqlCommand("UPDATE scazorla_sa.G_Activitats SET activa=0,updated_at=GETDATE() WHERE id=@Id", c);
        cmd.Parameters.AddWithValue("@Id", id); await cmd.ExecuteNonQueryAsync();
    }

    public async Task<ActivityDetails?> GetDetailsAsync(int id)
    {
        var activity = await GetAsync(id); if (activity is null) return null;
        await using var c = await connections.OpenAsync();
        const string sql = """
            SELECT i.id,i.activitat_id,i.soci_codi,s.FAMNom,s.FAMNIF,i.es_soci,i.pagat,
                   ISNULL(i.import_pagat,0),i.observacions
            FROM scazorla_sa.G_Activitats_Socis i
            INNER JOIN scazorla_sa.G_Socis s ON i.soci_codi=s.FAMID
            WHERE i.activitat_id=@Id AND i.activa=1 ORDER BY s.FAMNom
            """;
        await using var cmd = new SqlCommand(sql, c); cmd.Parameters.AddWithValue("@Id", id);
        var enrollments = new List<Enrollment>(); await using var r = await cmd.ExecuteReaderAsync();
        while (await r.ReadAsync()) enrollments.Add(new Enrollment
        {
            Id=r.GetInt32(0), ActivityId=r.GetInt32(1), MemberId=r.GetValue(2).ToString()!.Trim(),
            MemberName=r.GetString(3), Nif=r.IsDBNull(4)?null:r.GetString(4), IsMember=r.GetBoolean(5),
            Paid=r.GetBoolean(6), Amount=r.GetDecimal(7), Notes=r.IsDBNull(8)?null:r.GetString(8)
        });
        return new ActivityDetails { Activity=activity, Enrollments=enrollments };
    }

    public async Task AddEnrollmentAsync(int activityId, EnrollmentInput input)
    {
        await using var c = await connections.OpenAsync();
        const string sql = """
            IF EXISTS (SELECT 1 FROM scazorla_sa.G_Activitats_Socis WHERE activitat_id=@ActivityId AND soci_codi=@MemberId)
                UPDATE scazorla_sa.G_Activitats_Socis SET es_soci=@IsMember,import_pagat=@Amount,activa=1 WHERE activitat_id=@ActivityId AND soci_codi=@MemberId
            ELSE
                INSERT INTO scazorla_sa.G_Activitats_Socis (activitat_id,soci_codi,es_soci,import_pagat,pagat,activa) VALUES (@ActivityId,@MemberId,@IsMember,@Amount,0,1)
            """;
        await using var cmd = new SqlCommand(sql,c); cmd.Parameters.AddWithValue("@ActivityId",activityId);
        cmd.Parameters.AddWithValue("@MemberId",input.MemberId.Trim()); cmd.Parameters.AddWithValue("@IsMember",input.IsMember);
        cmd.Parameters.AddWithValue("@Amount",input.Amount); await cmd.ExecuteNonQueryAsync();
    }

    public async Task SetPaidAsync(int enrollmentId, bool paid)
    {
        await using var c=await connections.OpenAsync(); await using var cmd=new SqlCommand("UPDATE scazorla_sa.G_Activitats_Socis SET pagat=@Paid WHERE id=@Id",c);
        cmd.Parameters.AddWithValue("@Paid",paid); cmd.Parameters.AddWithValue("@Id",enrollmentId); await cmd.ExecuteNonQueryAsync();
    }

    public async Task RemoveEnrollmentAsync(int enrollmentId)
    {
        await using var c=await connections.OpenAsync(); await using var cmd=new SqlCommand("UPDATE scazorla_sa.G_Activitats_Socis SET activa=0 WHERE id=@Id",c);
        cmd.Parameters.AddWithValue("@Id",enrollmentId); await cmd.ExecuteNonQueryAsync();
    }

    private static Activity Map(SqlDataReader r)=>new()
    {
        Id=r.GetInt32(0),Description=r.GetString(1),StartDate=r.GetDateTime(2),EndDate=r.IsDBNull(3)?null:r.GetDateTime(3),
        MemberPrice=r.IsDBNull(4)?0:r.GetDecimal(4),NonMemberPrice=r.IsDBNull(5)?0:r.GetDecimal(5),
        Completed=r.GetBoolean(6),Active=r.GetBoolean(7)
    };
}
