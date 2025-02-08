CREATE TABLE ChatPartic (
	chat_id	INTEGER NOT NULL,
	user_id	INTEGER NOT NULL,	
	joined_at	DATETIME,
	FOREIGN KEY (chat_id) REFERENCES Chats(chat_id),
	FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
