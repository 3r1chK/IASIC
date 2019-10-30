
DROP DATABASE IF EXISTS marine_classification;

CREATE DATABASE marine_classification;

CREATE TABLE IF NOT EXISTS marine_classification.images
(
    _id                 INT(11) PRIMARY KEY AUTO_INCREMENT,
    predictions_id      INT(11) NOT NULL,
    location_id         INT(11),
    status              SET('VERIFIED', 'PENDING', 'UNCERTAIN') NOT NULL DEFAULT 'UNCERTAIN',
    is_human_verified   TINYINT(1) NOT NULL DEFAULT 0,
    insta_url           VARCHAR(256) NOT NULL,
    local_uri           VARCHAR(128) NOT NULL,
    sha256_digest       VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS marine_classification.predictions
(
    _id                 INT PRIMARY KEY AUTO_INCREMENT,
    prediction_id       INT NOT NULL,
    class_index         VARCHAR(32) NOT NULL,
    predicted_class     VARCHAR(64),
    probability         FLOAT(10,9) NOT NULL
);

CREATE TABLE IF NOT EXISTS marine_classification.locations
(
    _id             INT PRIMARY KEY AUTO_INCREMENT,
    name            CHAR(32) NOT NULL,
    latitude        CHAR(16) NOT NULL,
    longitude       CHAR(16) NOT NULL,
    locN            VARCHAR(32)
);
