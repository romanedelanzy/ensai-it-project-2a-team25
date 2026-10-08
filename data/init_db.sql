-----------------------------------------------------
-- Player
-----------------------------------------------------
DROP TABLE IF EXISTS player CASCADE;
CREATE TABLE player (
    id_player    SERIAL PRIMARY KEY,
    username     VARCHAR(30) UNIQUE,
    password     VARCHAR(256),
    elo          INTEGER,
    email        VARCHAR(50),
    pokemon_fan  BOOLEAN,
    access_token VARCHAR(255)
);

------------------------------------------------------------
-- Compte utilisateur
------------------------------------------------------------
DROP TABLE IF EXISTS compte CASCADE;
CREATE TABLE compte (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL
);

------------------------------------------------------------
-- Comptes utilisateurs de test
------------------------------------------------------------
INSERT INTO compte (username, is_admin, password_hash, email) VALUES 
('username1', TRUE, 'password_hash1', 'username1@email.fr'),
('username2', TRUE, 'password_hash2', 'username2@email.fr'),
('username3', FALSE, 'password_hash3', 'username3@email.fr'),
('username4', FALSE, 'password_hash4', 'username4@email.fr'),
('username5', FALSE, 'password_hash5', 'username5@email.fr'),
('username6', FALSE, 'password_hash6', 'username6@email.fr'),
('username7', FALSE, 'password_hash7', 'username7@email.fr'),
('username8', FALSE, 'password_hash8', 'username8@email.fr');