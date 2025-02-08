 
 CREATE TABLE Chats (
 chat_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
 chat_name TEXT, 
 created_by INTEGER,
 created_at INTEGER,
FOREIGN KEY (created_by) REFERENCES Users(user_id) ON DELETE CASCADE
  );