select
    player_name,
    champion_name,
    patch_version,
    count(*)                                        as games_played,
    sum(result)                                     as wins,
    round(sum(result)::numeric / count(*) * 100, 2) as win_rate_pct
from {{ ref('stg_matches') }}
group by
    player_name,
    champion_name,
    patch_version