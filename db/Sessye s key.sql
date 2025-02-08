select UserSessions.created_at, UserSessions.expires_at, UserSessions.user_id, UserSessions.token
from UserSessions
order by UserSessions.user_id