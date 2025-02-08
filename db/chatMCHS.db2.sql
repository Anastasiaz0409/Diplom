BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Users" (
	"user_id" SERIAL PRIMARY KEY UNIQUE,
	"username"	VARCHAR ( 30 ) NOT NULL,
	"password_hash"	VARCHAR ( 30 ),
	"role"	VARCHAR ( 50 ),
	"create_at"  TIMESTAMP,
	"update_at"	 TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "UserSessions" (
	"session_id" SERIAL PRIMARY KEY UNIQUE,
	"user_id"	INTEGER,
	"token"	Bytea,
	"created_at"	TIMESTAMP,
	"expires_at"	TIMESTAMP,
	FOREIGN KEY("user_id") REFERENCES "Users"("user_id")
);

CREATE TABLE IF NOT EXISTS "Chats" (
	"chat_id"	SERIAL PRIMARY KEY UNIQUE,
	"chat_name"	TEXT,
	"created_by"	INTEGER,
	"created_at"	TIMESTAMP,
	FOREIGN KEY("created_by") REFERENCES "Users"("user_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "Messages" (
	"message_id" SERIAL PRIMARY KEY UNIQUE,
	"chat_id"	INTEGER,
	"user_id"	INTEGER,
	"content"	Bytea,
	"timestamp"	TIMESTAMP,
	FOREIGN KEY("user_id") REFERENCES "Users"("user_id"),
	FOREIGN KEY("chat_id") REFERENCES "Chats"("chat_id")
);

CREATE TABLE IF NOT EXISTS "MesStatus" (
	"message_id"	INTEGER,
	"user_id"	INTEGER,
	"is_read"	BOOLEAN,
	"read_at"	TIMESTAMP,
	FOREIGN KEY("message_id") REFERENCES "Messages"("message_id"),
	FOREIGN KEY("user_id") REFERENCES "Users"("user_id")
);

CREATE TABLE IF NOT EXISTS "ChatPartic" (
	"chat_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"joined_at"	TIMESTAMP,
	FOREIGN KEY("chat_id") REFERENCES "Chats"("chat_id") ON DELETE CASCADE,
	FOREIGN KEY("user_id") REFERENCES "Users"("user_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "AuditLogs" (
	"log_id" SERIAL PRIMARY KEY UNIQUE,
	"user_id"	INTEGER,
	"action"	VARCHAR,
	"timestamp"	TIMESTAMP,
	FOREIGN KEY("user_id") REFERENCES "Users"("user_id")
);
COMMIT;
