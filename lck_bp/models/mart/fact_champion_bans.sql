with matches as (
    select * from {{ ref('stg_matches') }}
),

bans as (
    select match_id, patch_version, season_year, team_name, ban1 as champion_name from matches where ban1 is not null
    union all
    select match_id, patch_version, season_year, team_name, ban2 from matches where ban2 is not null
    union all
    select match_id, patch_version, season_year, team_name, ban3 from matches where ban3 is not null
    union all
    select match_id, patch_version, season_year, team_name, ban4 from matches where ban4 is not null
    union all
    select match_id, patch_version, season_year, team_name, ban5 from matches where ban5 is not null
),

final as (
    select
        champion_name,
        patch_version,
        season_year,
        count(*)                 as ban_count,
        count(distinct match_id) as games_appeared
    from bans
    group by
        champion_name,
        patch_version,
        season_year
)

select * from final
order by ban_count desc