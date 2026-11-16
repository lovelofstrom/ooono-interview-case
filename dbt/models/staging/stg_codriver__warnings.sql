select
    warning_id::uuid as warning_id,
    session_id::uuid as session_id,
    user_id,
    pin_type,
    device_time::timestamp as device_time,
    user_action,
    received_at::timestamptz as received_at
from {{ source('codriver', 'warnings') }}
-- Incremental loads can fetch the same warning twice. Keep the first one received per warning ID.
qualify row_number() over (partition by warning_id order by received_at) = 1
