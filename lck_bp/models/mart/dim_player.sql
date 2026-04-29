with int_player as (
    select * from {{ ref('int_player_history') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['player_name', 'valid_from']) }}
                                as player_sk,
        player_name,
        team_name,
        role,
        valid_from,
        valid_to,
        is_current,
        version_number
    from int_player
)

select * from final