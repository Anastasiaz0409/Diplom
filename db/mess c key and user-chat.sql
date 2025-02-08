Select  Chats.chat_name, Messages.user_id, Messages.timestamp, Messages.content, UserSessions.token,
	UserSessions.created_at, UserSessions.expires_at
        from Messages, Chats, UserSessions
        where Messages.chat_id = Chats.chat_id and UserSessions.user_id=Messages.user_id 
		and UserSessions.created_at <= Messages.timestamp and UserSessions.expires_at >= Messages.timestamp
		