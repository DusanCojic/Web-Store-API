CREATE DATABASE IF NOT EXISTS users;

USE users;

CREATE TABLE IF NOT EXISTS User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    forename VARCHAR(256) NOT NULL,
    surname VARCHAR(256) NOT NULL,
    email VARCHAR(256) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL,
    role ENUM('owner', 'customer', 'courier') NOT NULL
);

INSERT INTO User(forename, surname, email, password)
VALUES ("Scrooge", "McDuck", "onlymoney@gmail.com", "evenmoremoney");