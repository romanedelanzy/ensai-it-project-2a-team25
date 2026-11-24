INSERT INTO reseau(reseau_id, name) VALUES
(999, 'Réseau test A'),
(998, 'Réseau test B');

INSERT INTO station(station_id, reseau_id, name, adresse, latitude, longitude, capacite) VALUES
('TEST_001', 999, 'Alpha',   '1 rue Alpha, Paris',   48.8584,  2.3470, 30),
('TEST_002', 999, 'Bravo',   '2 rue Bravo, Paris',   48.8443,  2.3736, 40),
('TEST_003', 998, 'Charlie', NULL,                   45.7578,  4.8320, 20);

INSERT INTO compte (username, is_admin, password, email) VALUES 
('username1', TRUE, 'password1', 'username1@email.fr'),
('username2', TRUE, 'password2', 'username2@email.fr'),
('username3', FALSE, 'password3', 'username3@email.fr'),
('username4', FALSE, 'password4', 'username4@email.fr'),
('username5', FALSE, 'password5', 'username5@email.fr'),
('username6', FALSE, 'password6', 'username6@email.fr'),
('username7', FALSE, 'password7', 'username7@email.fr'),
('username8', FALSE, 'password8', 'username8@email.fr');