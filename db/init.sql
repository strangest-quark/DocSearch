CREATE DATABASE search;
use search;

CREATE TABLE s3_connections(name VARCHAR(50) NOT NULL UNIQUE, access_key_id TEXT NOT NULL, access_key TEXT NOT NULL, bucket TEXT NOT NULL, region TEXT NOT NULL, PRIMARY KEY(name));

CREATE TABLE tags(name VARCHAR(50) NOT NULL UNIQUE,  tags TEXT NOT NULL, PRIMARY KEY(name));