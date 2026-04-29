with matches as (
    select * from {{ ref('stg_matches') }}
),

final as (
    select
        player_name,
        team_name,
        role,
        side,
        patch_version,

        -- 出場數
        count(*)                                                as games_played,

        -- KDA
        round(avg(
            (kills + assists) / nullif(deaths, 0)
        )::numeric, 2)                                         as avg_kda,

        -- 場均 K+A
        round(avg(kills + assists)::numeric, 2)                as avg_ka,

        -- 場均死亡
        round(avg(deaths)::numeric, 2)                         as avg_deaths,

        -- 分均傷害
        round(avg(
            damagetochampions / nullif(game_duration_seconds / 60.0, 0)
        )::numeric, 2)                                         as dpm,

        -- 傷害占比
        round(avg(damageshare) * 100, 2)                       as avg_damage_share,

        -- 傷轉（每分鐘承傷）
        round(avg(damagetakenperminute)::numeric, 2)           as dtpm,

        -- 分均補刀
        round(avg(cspm)::numeric, 2)                           as avg_cspm,

        -- 分均經濟
        round(avg(
            earnedgold / nullif(game_duration_seconds / 60.0, 0)
        )::numeric, 2)                                         as egpm,

        -- 經濟占比
        round(avg(earnedgoldshare) * 100, 2)                   as avg_gold_share,

        -- 勝率
        round(sum(result)::numeric / count(*) * 100, 2)        as win_rate_pct

    from matches
    group by
        player_name,
        team_name,
        role,
        side,
        patch_version
)

select * from final
order by player_name, patch_version