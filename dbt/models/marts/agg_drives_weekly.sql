with drives as (
    select *
    from {{ ref('fct_drives') }}
    where user_id != 'unauthenticated'
),

users as (
    select
        week,
        platform,
        app_version,
        os_version,
        user_id,
        plan,
        monthly_price_eur,
        bool_or(restarted_within_30s) as had_broken_drive
    from drives
    group by all
),

drive_counts as (
    select
        week,
        platform,
        app_version,
        os_version,
        count(*) as drives,
        count_if(restarted_within_30s) as broken_drives,
        count_if(has_multiple_connections) as drives_with_multiple_connections
    from drives
    group by all
),

user_counts as (
    select
        week,
        platform,
        app_version,
        os_version,
        count(*) as users,
        count_if(had_broken_drive) as users_with_broken_drives,
        count_if(had_broken_drive and plan = 'premium') as premium_users_with_broken_drives,
        sum(
            case
                when had_broken_drive
                and plan = 'premium'
                    then monthly_price_eur
                else 0
            end
        ) as affected_premium_monthly_revenue_eur
    from users
    group by all
)

select
    drive_counts.week,
    drive_counts.platform,
    drive_counts.app_version,
    drive_counts.os_version,
    drive_counts.drives,
    drive_counts.broken_drives,
    drive_counts.drives_with_multiple_connections,
    user_counts.users,
    user_counts.users_with_broken_drives,
    user_counts.premium_users_with_broken_drives,
    user_counts.affected_premium_monthly_revenue_eur
from drive_counts
inner join user_counts
    on drive_counts.week = user_counts.week
    and drive_counts.platform = user_counts.platform
    and drive_counts.app_version = user_counts.app_version
    and drive_counts.os_version = user_counts.os_version
