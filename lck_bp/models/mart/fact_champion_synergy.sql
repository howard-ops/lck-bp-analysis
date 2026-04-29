with matches as (
    select * from {{ ref('stg_matches') }}
),

-- 把同一場比賽的英雄兩兩配對
pairs as (
    select
        a.match_id,
        a.patch_version,
        a.season_year,
        a.champion_name     as champion_a,
        b.champion_name     as champion_b,
        a.team_name         as team_a,
        b.team_name         as team_b,
        a.result            as result_a
    from matches a
    join matches b
        on  a.match_id      = b.match_id
        and a.champion_name != b.champion_name
),

-- 分成同隊（synergy）和對手（counter）兩種關係
classified as (
    select
        champion_a,
        champion_b,
        patch_version,
        season_year,
        case
            when team_a = team_b then 'synergy'
            else 'counter'
        end                 as relationship,
        result_a            as result
    from pairs
),

final as (
    select
        champion_a,
        champion_b,
        patch_version,
        season_year,
        relationship,
        count(*)            as games_together,
        sum(result)         as wins,
        round(
            sum(result)::numeric / count(*) * 100
        , 2)                as win_rate_pct
    from classified
    group by
        champion_a,
        champion_b,
        patch_version,
        season_year,
        relationship
)

select * from final
order by relationship, win_rate_pct desc