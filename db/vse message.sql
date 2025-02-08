
SELECT "Chats".chat_name, "Messages".timestamp, "Users".username, "Messages".content, "UserSessions".token, "UserSessions".created_at, "UserSessions".expires_at 
FROM "Chats" JOIN "Messages" ON "Chats".chat_id = "Messages".chat_id JOIN "Users" ON "Users".user_id = "Messages".user_id, "UserSessions" 
WHERE "UserSessions".user_id = "Messages".user_id AND "Messages".timestamp >= "UserSessions".created_at AND 
("Messages".timestamp <= "UserSessions".expires_at OR "UserSessions".expires_at IS NULL)
