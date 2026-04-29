with stg as (
    select * from {{ ref('stg_matches') }}
),

player_versions as (
    select
        player_name,
        team_name,
        role,
        min(match_date)  as valid_from,
        max(match_date)  as valid_to
    from stg
    group by
        player_name,
        team_name,
        role
),

scd_logic as (
    select
        player_name,
        team_name,
        role,
        valid_from,
        lead(valid_from) over (
            partition by player_name
            order by valid_from
        ) as next_valid_from,
        valid_to,
        row_number() over (
            partition by player_name
            order by valid_from
        ) as version_number
    from player_versions
),

final as (
    select
        player_name,
        team_name,
        role,
        valid_from,
        coalesce(next_valid_from - interval '1 day', date '9999-12-31') as valid_to,
        case
            when next_valid_from is null then true
            else false
        end                          as is_current,
        version_number
    from scd_logic
)

select * from final