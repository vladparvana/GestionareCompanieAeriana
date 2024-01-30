

CREATE SEQUENCE utilizatori_seq
  START WITH 1
  INCREMENT BY 1
  NOMAXVALUE
  NOCYCLE;


CREATE SEQUENCE rute_seq
  START WITH 1
  INCREMENT BY 1
  NOMAXVALUE
  NOCYCLE;

CREATE SEQUENCE zboruri_seq
  START WITH 1
  INCREMENT BY 1
  NOMAXVALUE
  NOCYCLE;

CREATE SEQUENCE bagajcala_seq
  START WITH 1
  INCREMENT BY 1
  NOMAXVALUE
  NOCYCLE;


CREATE TABLE Utilizatori (
    UserID INTEGER DEFAULT utilizatori_seq.NEXTVAL PRIMARY KEY,
    Nume VARCHAR2(40) NOT NULL,
    Prenume VARCHAR2(40) NOT NULL,
    DataNastere DATE NOT NULL,
    Email VARCHAR2(100) NOT NULL,
    Parola VARCHAR2(250) NOT NULL,
    Sarea VARCHAR(250) NOT NULL,
    Admin VARCHAR2(3) CHECK (admin IN ('DA', 'NU'))
);

CREATE TABLE Rute (
    RutaID INTEGER DEFAULT rute_seq.NEXTVAL PRIMARY KEY,
    OrasPlecare VARCHAR2(50) NOT NULL,
    OrasDestinatie VARCHAR2(50) NOT NULL,
    Distanta NUMBER CHECK (Distanta > 0) NOT NULL,
    DurataEstimata DECIMAL(10, 2) CHECK (DurataEstimata > 0) NOT NULL
);

CREATE TABLE Zboruri (
    ZborID INTEGER DEFAULT zboruri_seq.NEXTVAL PRIMARY KEY,
    RutaID INTEGER,
    DataPlecare DATE NOT NULL,
    LocuriDisponibile NUMBER CHECK (LocuriDisponibile >= 0 ) NOT NULL,
    PretBilet DECIMAL(10, 2) CHECK (PretBilet > 0) NOT NULL,
    BagajCala VARCHAR2(3) CHECK (BagajCala IN ('DA', 'NU')),
    FOREIGN KEY (RutaID) REFERENCES Rute(RutaID)
);

CREATE TABLE DetaliiBagajCala (
    DetaliiBagajCalaID INTEGER DEFAULT bagajcala_seq.NEXTVAL PRIMARY KEY,
    ZborID NUMBER UNIQUE,
    GreutateBagaj NUMBER CHECK (GreutateBagaj>0) NOT NULL,
    GreutateMaxima NUMBER CHECK (GreutateMaxima >= 0)NOT NULL,
    Dimensiuni VARCHAR2(20) ,
    PretBagaj DECIMAL(10, 2) CHECK (PretBagaj > 0) NOT NULL,
    FOREIGN KEY (ZborID) REFERENCES Zboruri(ZborID)
);



CREATE TABLE Bilete (
    BiletID NUMBER,
    ZborID NUMBER,
    UserID NUMBER,
    Loc NUMBER,
    DataCumparare DATE DEFAULT CURRENT_DATE,
    PretBilet DECIMAL(10, 2),
    Stare VARCHAR2(10) DEFAULT 'Valabil' CHECK (Stare IN ('Valabil', 'Cumparat')),
    BagajCala CHAR(2) DEFAULT 'NU' CHECK (BagajCala IN ('DA', 'NU')),
    PRIMARY KEY (BiletID, ZborID),
    FOREIGN KEY (UserID) REFERENCES Utilizatori(UserID) ON DELETE SET NULL,
    FOREIGN KEY (ZborID) REFERENCES Zboruri(ZborID)
);

COMMIT;


