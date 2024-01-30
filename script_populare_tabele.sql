-- Popularea tabelului Utilizatori
-- pentru utlizatori parola este "user" , iar pentru administratori este "admin"
INSERT INTO Utilizatori (UserID, Nume, Prenume, DataNastere, Email, Parola, Sarea, Admin)
VALUES
(1, 'Parvana', 'Vlad', TO_DATE('27-NOV-02', 'DD-MON-RR'), 'vlad-stefan.parvana@student.tuiasi.ro', '$2b$12$tK1aGdM5UZcM7hvg7OvNW.bhdSmQ77NsdsAPYMbWmzr0CvpSiacqe', '$2b$12$tK1aGdM5UZcM7hvg7OvNW.', 'DA');

INSERT INTO Utilizatori (UserID, Nume, Prenume, DataNastere, Email, Parola, Sarea, Admin)
VALUES
(2, 'Vartolomei', 'Mihai', TO_DATE('13-FEB-02', 'DD-MON-RR'), 'mihai-sebastian.vartolomei@student.tuias.ro', '$2b$12$/2EPFudnYcmctnAnO2Hk4.s6qgZ/DZgrbdKK6epTTcF1stjp5gP96', '$2b$12$/2EPFudnYcmctnAnO2Hk4.', 'DA');

INSERT INTO Utilizatori (UserID, Nume, Prenume, DataNastere, Email, Parola, Sarea, Admin)
VALUES
(3, 'Utilizator', 'Unu', TO_DATE('01-JAN-01', 'DD-MON-RR'), 'utlizator1@tarom.com', '$2b$12$VitUoTfhwhkNx/di1ilF1Oy4PQArtL.IEk.dAV4DUMLKdL/tXN2NC', '$2b$12$VitUoTfhwhkNx/di1ilF1O', 'NU');

INSERT INTO Utilizatori (UserID, Nume, Prenume, DataNastere, Email, Parola, Sarea, Admin)
VALUES
(4, 'Utilizator', 'Doi', TO_DATE('02-FEB-02', 'DD-MON-RR'), 'utilizator@tarom.com', '$2b$12$tOk7f.ykDRIlwB0BFdoOw.fGhRX8ETzGiBxLCqbXYtI2zgFwO.K/S', '$2b$12$tOk7f.ykDRIlwB0BFdoOw.', 'NU');

INSERT INTO Utilizatori (UserID, Nume, Prenume, DataNastere, Email, Parola, Sarea, Admin)
VALUES
(5, 'Utilizator', 'Trei', TO_DATE('03-MAR-03', 'DD-MON-RR'), 'utilizator3@tarom.com', '$2b$12$hymFnn9DfUjAPkDyJ6m6POu1/uD371LAMXUdGzdSPF9AGr9tlFUVu', '$2b$12$hymFnn9DfUjAPkDyJ6m6PO', 'NU');


-- Popularea tabelului Rute cu valori specifice pentru RutaID
INSERT INTO Rute (RutaID, OrasPlecare, OrasDestinatie, Distanta, DurataEstimata)
VALUES (6, 'Iasi', 'Bucuresti', 400, 1.5);

INSERT INTO Rute (RutaID, OrasPlecare, OrasDestinatie, Distanta, DurataEstimata)
VALUES (7, 'Iasi', 'Cluj', 380, 1.6);

INSERT INTO Rute (RutaID, OrasPlecare, OrasDestinatie, Distanta, DurataEstimata)
VALUES (8, 'Bucuresti', 'Madrid', 1500, 4);

INSERT INTO Rute (RutaID, OrasPlecare, OrasDestinatie, Distanta, DurataEstimata)
VALUES (9, 'Iasi', 'Timisoara', 450, 2);

INSERT INTO Rute (RutaID, OrasPlecare, OrasDestinatie, Distanta, DurataEstimata)
VALUES (10, 'Iasi', 'Munchen', 800, 2);



-- Popularea tabelului Zboruri
INSERT INTO Zboruri (ZborID, RutaID, DataPlecare, LocuriDisponibile, PretBilet, BagajCala)
VALUES (4, 6, TO_DATE('10-JAN-24', 'DD-MON-YY'), 1, 110, 'DA');

INSERT INTO Zboruri (ZborID, RutaID, DataPlecare, LocuriDisponibile, PretBilet, BagajCala)
VALUES (2, 6, TO_DATE('08-JAN-24', 'DD-MON-YY'), 1, 100, 'DA');

INSERT INTO Zboruri (ZborID, RutaID, DataPlecare, LocuriDisponibile, PretBilet, BagajCala)
VALUES (3, 7, TO_DATE('08-JAN-24', 'DD-MON-YY'), 1, 150, 'DA');

INSERT INTO Zboruri (ZborID, RutaID, DataPlecare, LocuriDisponibile, PretBilet, BagajCala)
VALUES (5, 8, TO_DATE('08-JAN-24', 'DD-MON-YY'), 1, 100, 'DA');

INSERT INTO Zboruri (ZborID, RutaID, DataPlecare, LocuriDisponibile, PretBilet, BagajCala)
VALUES (6, 6, TO_DATE('17-JAN-24', 'DD-MON-YY'), 1, 200, 'DA');

-- Popularea tabelului DetaliiBagajCala
INSERT INTO DetaliiBagajCala (DetaliiBagajCalaID, ZborID, GreutateBagaj, GreutateMaxima, Dimensiuni, PretBagaj)
VALUES (1, 2, 20, 40, '50x80x25', 50);

INSERT INTO DetaliiBagajCala (DetaliiBagajCalaID, ZborID, GreutateBagaj, GreutateMaxima, Dimensiuni, PretBagaj)
VALUES (2, 3, 15, 75, NULL, 60);

INSERT INTO DetaliiBagajCala (DetaliiBagajCalaID, ZborID, GreutateBagaj, GreutateMaxima, Dimensiuni, PretBagaj)
VALUES (3, 4, 10, 80, NULL, 25);

INSERT INTO DetaliiBagajCala (DetaliiBagajCalaID, ZborID, GreutateBagaj, GreutateMaxima, Dimensiuni, PretBagaj)
VALUES (4, 5, 20, 600, '60x120x35', 45);

INSERT INTO DetaliiBagajCala (DetaliiBagajCalaID, ZborID, GreutateBagaj, GreutateMaxima, Dimensiuni, PretBagaj)
VALUES (5, 6, 25, 50, NULL, 40);


-- Popularea tabelului Bilete
INSERT INTO Bilete (BiletID, ZborID, UserID, Loc, DataCumparare, PretBilet, Stare, BagajCala)
VALUES (1, 2, NULL, 2, TO_DATE('07-JAN-24', 'DD-MON-YY'), NULL, 'Valabil', 'NU');

INSERT INTO Bilete (BiletID, ZborID, UserID, Loc, DataCumparare, PretBilet, Stare, BagajCala)
VALUES (1, 3, NULL, 2, TO_DATE('07-JAN-24', 'DD-MON-YY'), NULL, 'Valabil', 'NU');

INSERT INTO Bilete (BiletID, ZborID, UserID, Loc, DataCumparare, PretBilet, Stare, BagajCala)
VALUES (1, 4, NULL, 2, TO_DATE('07-JAN-24', 'DD-MON-YY'), NULL, 'Valabil', 'NU');

INSERT INTO Bilete (BiletID, ZborID, UserID, Loc, DataCumparare, PretBilet, Stare, BagajCala)
VALUES (1, 5, NULL, 2, TO_DATE('07-JAN-24', 'DD-MON-YY'), NULL, 'Valabil', 'NU');

INSERT INTO Bilete (BiletID, ZborID, UserID, Loc, DataCumparare, PretBilet, Stare, BagajCala)
VALUES (1, 6, NULL, 2, TO_DATE('07-JAN-24', 'DD-MON-YY'), NULL, 'Valabil', 'NU');

COMMIT;

