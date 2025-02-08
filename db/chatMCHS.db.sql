BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `Users` (
	`user_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`username`	varchar ( 30 ) NOT NULL,
	`password_hash`	VARCHAR ( 30 ),
	`role`	VARCHAR ( 50 ),
	`create_at`	DATETIME,
	`update_at`	DATETIME
);
INSERT INTO `Users` (user_id,username,password_hash,role,create_at,update_at) VALUES (1,'maria.vasileva','Maria@2024','администратор','2024.11.01','2024.11.01'),
 (2,'sergey.morozov','Sergey#1234','сотрудник','2024.11.03','2024.11.03'),
 (3,'elena.kovaleva','Elena!5678','сотрудник','2024.11.03','2024.11.03'),
 (4,'viktoria.mikhailova','Viktoria@7890','сотрудник','2024.11.05','2024.11.05'),
 (5,'nikolay.fedorov','Nikolay$2024','сотрудник','2024.11.09','2024.11.09'),
 (6,'ivan.petrov','Ivan2024!','сотрудник','2024.11.10','2024.11.10'),
 (7,'anna.smirnova','Anna@1234','сотрудник','2024.11.10','2024.11.10'),
 (8,'dmitry.ivanov','Dmitry!5678','сотрудник','2024.11.12','2024.11.12'),
 (9,'olga.sokolova','Olga#2024','сотрудник','2024.11.12','2024.11.12'),
 (10,'alexey.kuznetsov','Alexey$7890','сотрудник','2024.11.12','2024.11.12');
CREATE TABLE IF NOT EXISTS `UserSessions` (
	`session_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`user_id`	INTEGER,
	`token`	BLOB,
	`created_at`	DATETIME,
	`expires_at`	DATETIME,
	FOREIGN KEY(`user_id`) REFERENCES `Users`(`user_id`)
);
INSERT INTO `UserSessions` (session_id,user_id,token,created_at,expires_at) VALUES (1,1,'8C|��=8$y�FKs~�>PQ���,���pW졌�','2024.11.15 09:42:21','2024.11.15 09:45:21'),
 (2,10,'��ڊ(���j�>2&���ás�V��#��7�','2024.11.22','2024.11.22'),
 (3,3,'��xǷν���l�y,� ���	#6�4�#�7','2024.11.20 14:23:30','2024.11.20 14:25:30'),
 (5,1,'8C|��=8$y�FKs~�>PQ���,���pW졌�','2024.12.10 11:42:21','2024.12.10 11:50:21'),
 (6,2,'��l׭w�Zɮ�W���j�5��b�z"�+����,�','2024.12.10 11:42:21',NULL),
 (7,2,'��l׭w�Zɮ�W���j�5��b�z"�+����,�','2024.12.10 12:01:24',NULL),
 (8,2,'��l׭w�Zɮ�W���j�5��b�z"�+����,�','2024.12.10 12:03:42',NULL),
 (9,7,'�٬��S��{s
Ih���P\�9���Qmy�"','2024.12.10 12:07:40',NULL),
 (10,7,'�٬��S��{s
Ih���P\�9���Qmy�"','2024.12.10 12:11:24',NULL),
 (11,3,'��xǷν���l�y,� ���	#6�4�#�7','2024.12.10 14:22:38','2024.12.10 14:25:38'),
 (12,1,'8C|��=8$y�FKs~�>PQ���,���pW졌�','2024.12.10 15:11:53','2024.12.10 15:20:53');
CREATE TABLE IF NOT EXISTS `Messages` (
	`message_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`chat_id`	INTEGER,
	`user_id`	INTEGER,
	`content`	BLOB,
	`timestamp`	DATETIME,
	FOREIGN KEY(`user_id`) REFERENCES `Users`(`user_id`),
	FOREIGN KEY(`chat_id`) REFERENCES `Chats`(`chat_id`)
);
INSERT INTO `Messages` (message_id,chat_id,user_id,content,timestamp) VALUES (1,1,1,'�矠l;W�yf��{�6�[�W���H��K��81�..�n��>-��?�{����#6�a�5��~�LҙqX�8��X�V�','2024.11.15 09:44:21'),
 (2,2,3,'��}�|�����LG��I��TѼN�Ϩ#���Y���0�#l"C�0ܴ��:ѐ�ʄ�4�r��6�˶�������m=�]��q�c4H�G;S�f�B��hX h�˞��X�, ;�U�(�wϭ���Ƽ�����	��Ϗ2"�TJ	��CK<W%x������I�Oh."r��x1���I�''�"Ѵ�;ik�s�_��UZ&��D�Z�x����	�}���Q��U���������@e��]5��=̹��mˡPq�boD��?��)ȳ.�R��V=��i3F��%���{.M��s�a�����','2024.11.20 14:24:30'),
 (3,3,10,'c
����vSj
�
�}t�K���OZ>�{V�lZ�[�L�A�oJ''!R��0�O�Q9����E�պ���2��v��p��,�q=�2b�^^Hy6������U]��"<��81X+�����AΨ�OA�{3q�,��к�wpe��k&�2WYl�R�8�O29c���y�($>+���i�����<B� ��	<Y�$���`>Y�''q�aK]�^r�2Yn�Vr�J����','2024.11.22'),
 (4,1,7,'�uu��J9p�A��:�_���%֓8b��O���','2024.12.10 12:07:55'),
 (5,1,7,'h*������`G�%��J��
*8����6nf3','2024.12.10 12:20:39'),
 (6,1,3,',�����Fx��~KV)C䒑�d����՗F��{��
bC��R�@��]�','2024.12.10 14:24:30');
CREATE TABLE IF NOT EXISTS `MesStatus` (
	`message_id`	INTEGER,
	`user_id`	INTEGER,
	`is_read`	BOOLEAN,
	`read_at`	DATETIME,
	FOREIGN KEY(`message_id`) REFERENCES `Messages`(`message_id`),
	FOREIGN KEY(`user_id`) REFERENCES `Users`(`user_id`)
);
INSERT INTO `MesStatus` (message_id,user_id,is_read,read_at) VALUES (1,1,0,''),
 (2,3,0,''),
 (3,10,0,'');
CREATE TABLE IF NOT EXISTS `Chats` (
	`chat_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`chat_name`	TEXT,
	`created_by`	INTEGER,
	`created_at`	INTEGER,
	FOREIGN KEY(`created_by`) REFERENCES `Users`(`user_id`) ON DELETE CASCADE
);
INSERT INTO `Chats` (chat_id,chat_name,created_by,created_at) VALUES (1,'general',1,'2024.11.15'),
 (2,'operation_head',3,'2024.11.18'),
 (3,'rescuers',10,'2024.11.20');
CREATE TABLE IF NOT EXISTS `ChatPartic` (
	`chat_id`	INTEGER NOT NULL,
	`user_id`	INTEGER NOT NULL,
	`joined_at`	DATETIME,
	FOREIGN KEY(`chat_id`) REFERENCES `Chats`(`chat_id`) ON DELETE CASCADE,
	FOREIGN KEY(`user_id`) REFERENCES `Users`(`user_id`) ON DELETE CASCADE
);
INSERT INTO `ChatPartic` (chat_id,user_id,joined_at) VALUES (1,1,NULL),
 (1,2,NULL),
 (1,3,NULL),
 (1,4,NULL),
 (1,5,NULL),
 (1,6,NULL),
 (1,7,NULL),
 (1,8,NULL),
 (1,9,NULL),
 (1,10,NULL),
 (3,10,NULL),
 (3,8,NULL),
 (2,3,NULL),
 (2,2,NULL),
 (2,5,NULL);
CREATE TABLE IF NOT EXISTS `AuditLogs` (
	`log_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`user_id`	INTEGER,
	`action`	VARCHAR,
	`timestamp`	DATETIME,
	FOREIGN KEY(`user_id`) REFERENCES `Users`(`user_id`)
);
COMMIT;
