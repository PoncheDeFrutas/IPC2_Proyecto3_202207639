-- schema.sql

-- Tabla "positive_feelings"
CREATE TABLE IF NOT EXISTS positive_feelings (
    id INTEGER PRIMARY KEY,
    feeling TEXT NOT NULL
);

-- Tabla "negative_feelings"
CREATE TABLE IF NOT EXISTS negative_feelings (
    id INTEGER PRIMARY KEY,
    feeling TEXT NOT NULL
);

-- Tabla "positive_rejected"
CREATE TABLE IF NOT EXISTS positive_rejected (
    id INTEGER PRIMARY KEY,
    feeling TEXT NOT NULL
);

-- Tabla "negative_rejected"
CREATE TABLE IF NOT EXISTS negative_rejected (
    id INTEGER PRIMARY KEY,
    feeling TEXT NOT NULL
);

-- Tabla "dictionary"
CREATE TABLE IF NOT EXISTS dictionary (
    id INTEGER PRIMARY KEY,
    id_positive_feelings INTEGER,
    id_negative_feelings INTEGER,
    id_positive_rejected INTEGER,
    id_negative_rejected INTEGER,
    FOREIGN KEY (id_positive_feelings) REFERENCES positive_feelings (id),
    FOREIGN KEY (id_negative_feelings) REFERENCES negative_feelings (id),
    FOREIGN KEY (id_positive_rejected) REFERENCES positive_rejected (id),
    FOREIGN KEY (id_negative_rejected) REFERENCES negative_rejected (id)
);

-- Tabla "users"
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    users TEXT
);

-- Tabla "hashtags"
CREATE TABLE IF NOT EXISTS hashtags (
    id INTEGER PRIMARY KEY,
    hashtags TEXT
);

-- Tabla "messages"
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    date_ TEXT NOT NULL,
    text TEXT NOT NULL,
    dd_mm_yyyy TEXT NOT NULL
);

-- Tabla "messages_users" para relacionar mensajes con usuarios
CREATE TABLE IF NOT EXISTS messages_users (
    id INTEGER PRIMARY KEY,
    message_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (message_id) REFERENCES messages (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Tabla "messages_hashtags" para relacionar mensajes con hashtags
CREATE TABLE IF NOT EXISTS messages_hashtags (
    id INTEGER PRIMARY KEY,
    message_id INTEGER,
    hashtag_id INTEGER,
    FOREIGN KEY (message_id) REFERENCES messages (id),
    FOREIGN KEY (hashtag_id) REFERENCES hashtags (id)
);

