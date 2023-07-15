CREATE DATABASE IF NOT EXISTS mydb;
USE mydb;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

INSERT IGNORE INTO users (username, password) values ("Paneer", "password");
INSERT IGNORE INTO users (username, password) values ("friend1", "password");
INSERT IGNORE INTO users (username, password) values ("friend2", "password");