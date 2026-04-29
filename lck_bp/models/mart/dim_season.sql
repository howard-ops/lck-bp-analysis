select distinct
    extract(year from match_date::date)::integer as season_year
from {{ ref('stg_matches') }}
order by season_year