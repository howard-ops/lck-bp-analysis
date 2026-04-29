with patches as (
    select
        patch_version,
        min(match_date) as first_seen
    from {{ ref('stg_matches') }}
    group by patch_version
),

ranked as (
    select
        patch_version,
        first_seen,
        row_number() over (
            order by first_seen desc
        ) as recency_rank
    from patches
),

weighted as (
    select
        patch_version,
        first_seen,
        recency_rank,
        round(
            1.0 / recency_rank
        , 4)                as patch_weight
    from ranked
)

select * from weighted
order by recency_rank