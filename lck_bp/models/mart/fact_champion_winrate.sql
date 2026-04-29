with matches as (
    select * from {{ ref('stg_matches') }}
),

winrate as (
    select
        champion_name,
        role,
        patch_version,
        count(*)                                    as games_played,
        sum(result)                                 as wins,
        round(
            sum(result)::numeric / count(*) * 100
        , 2)                                        as win_rate_pct
    from matches
    group by
        champion_name,
        role,
        patch_version
)

select * from winrate
order by win_rate_pct desc