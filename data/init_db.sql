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
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    access_token VARCHAR(255)

);

------------------------------------------------------------
-- Réseau
------------------------------------------------------------
DROP TABLE IF EXISTS reseau CASCADE;
CREATE TABLE reseau (
    reseau_id SERIAL PRIMARY KEY,
    name      VARCHAR(100) NOT NULL UNIQUE
);

------------------------------------------------------------
-- Station
------------------------------------------------------------
DROP TABLE IF EXISTS station CASCADE;
CREATE TABLE station (
    station_id VARCHAR(50) PRIMARY KEY,
    reseau_id  INTEGER NOT NULL REFERENCES reseau(reseau_id) ON DELETE CASCADE,
    name       VARCHAR(150) NOT NULL,
    adresse    VARCHAR(255),
    latitude   DOUBLE PRECISION NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude  DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    capacite   INTEGER NOT NULL CHECK (capacite >= 0)
);

------------------------------------------------------------
-- Favoris
------------------------------------------------------------
DROP TABLE IF EXISTS favoris CASCADE;
CREATE TABLE favoris (
    user_id    INTEGER     NOT NULL REFERENCES compte(user_id)    ON DELETE CASCADE,
    station_id VARCHAR(50) NOT NULL REFERENCES station(station_id) ON DELETE CASCADE,
    create_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, station_id)
);

------------------------------------------------------------
-- StationStatus
------------------------------------------------------------

DROP TABLE IF EXISTS station_status CASCADE;
CREATE TABLE station_status (
    station_id              VARCHAR(50) NOT NULL REFERENCES station(station_id),
    last_reported           TIMESTAMPTZ NOT NULL,
    num_bike_available      INTEGER,
    num_bike_elec_available INTEGER,
    num_docks_available     INTEGER,
    is_installed            BOOLEAN,
    is_renting              BOOLEAN,
    is_returning            BOOLEAN,
    PRIMARY KEY (station_id, last_reported)
);