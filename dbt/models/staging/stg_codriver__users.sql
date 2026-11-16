select
    user_id,
    created_at::timestamptz as created_at,
    country,
    platform,
    plan,
    monthly_price_eur::decimal(10, 2) as monthly_price_eur
from {{ source('codriver', 'users') }}
-- Users are fetched as a full snapshot every run. Keep each user's most recent snapshot.
qualify row_number() over (partition by user_id order by filename desc) = 1
