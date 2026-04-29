with winrate as (
    select * from {{ ref('fact_champion_winrate') }}
),

weights as (
    select * from {{ ref('fact_patch_weights') }}
),

-- 把勝率和版本權重合併
joined as (
    select
        w.champion_name,
        w.role,
        w.patch_version,
        w.games_played,
        w.win_rate_pct,
        p.patch_weight,
        w.win_rate_pct * p.patch_weight   as weighted_score
    from winrate w
    join weights p
        on w.patch_version = p.patch_version
),

-- 計算每個英雄跨版本的加權勝率
final as (
    select
        champion_name,
        role,
        round(
            sum(weighted_score) / sum(patch_weight)
        , 2)                                as weighted_win_rate,
        sum(games_played)                   as total_games,
        max(patch_version)                  as latest_patch,
        count(distinct patch_version)       as patches_tracked
    from joined
    group by
        champion_name,
        role
)

select * from final
where total_games >= 10
order by weighted_win_rate desc