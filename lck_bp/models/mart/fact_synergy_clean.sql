select
    champion_a,
    champion_b,
    relationship,
    season_year,
    win_rate_pct,
    games_together
from {{ ref('fact_champion_synergy') }}
where games_together >= 5
  and champion_a < champion_b