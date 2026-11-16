select
    session_id::uuid as session_id,
    user_id,
    platform,
    app_version,
    os_version,
    device,
    country,
    started_at::timestamp as started_at,
    ended_at::timestamp as ended_at,
    duration_s::integer as duration_s,
    connection_count::integer as connection_count,
    received_at::timestamptz as received_at
from {{ source('codriver', 'drives') }}
-- Drive reports can be resent. Keep the first one received per session ID.
qualify row_number() over (partition by session_id order by received_at) = 1
