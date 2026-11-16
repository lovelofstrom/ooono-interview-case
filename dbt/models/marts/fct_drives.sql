with drives as (
    select
        *,
        lead(started_at) over (partition by user_id order by started_at) as next_started_at
    from {{ ref('stg_codriver__drives') }}
)

select
    drives.session_id,
    drives.user_id,
    drives.platform,
    drives.app_version,
    drives.os_version,
    drives.device,
    drives.country,
    users.plan,
    users.monthly_price_eur,
    drives.started_at,
    drives.ended_at,
    date_trunc('week', drives.started_at)::date as week,
    drives.duration_s,
    drives.connection_count,
    drives.received_at,
    drives.connection_count > 1 as has_multiple_connections,
    case
        -- All unauthenticated drives share one `user_id`, so their
        -- `next_started_at` comes from unrelated drives. Keep them in the
        -- model but `null` the flag to avoid misleading analyses.
        when drives.user_id = 'unauthenticated'
            then null
        -- In the data up to 2026-11-15, gaps of 0-29 s to the user's next
        -- drive were ~20x more common than any later 30s window up to 15
        -- minutes, dropping off sharply at 30s, so they're treated as
        -- cut-outs.
        when date_diff('second', drives.ended_at, drives.next_started_at) between 0 and 29
            then true
        else false
    end as restarted_within_30s
from drives
left join {{ ref('stg_codriver__users') }} as users
    on drives.user_id = users.user_id
