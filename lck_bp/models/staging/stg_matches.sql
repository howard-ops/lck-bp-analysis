with source as (
    select * from {{ source('lck_raw', 'raw_matches') }}
),

renamed as (
    select
        gameid                              as match_id,
        date                                as match_date,
        patch                               as patch_version,
        teamname                            as team_name,
        playername                          as player_name,
        position                            as role,
        champion                            as champion_name,
        result                              as result,
        gamelength                          as game_duration_seconds,
        side                                as side,
        kills                               as kills,
        deaths                              as deaths,
        assists                             as assists,
        damagetochampions                   as damagetochampions,
        damageshare                         as damageshare,
        damagetakenperminute                as damagetakenperminute,
        damagemitigatedperminute            as damagemitigatedperminute,
        cspm                                as cspm,
        earnedgold                          as earnedgold,
        earnedgoldshare                     as earnedgoldshare,
        total_cs                            as total_cs
    from source
)

select * from renamed