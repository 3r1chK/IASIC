# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                               #
#     Copyright 2019 Erich Kohmann                                              #
#                                                                               #
#     This file is part of IASIC.                                               #
#                                                                               #
#     IASIC is free software: you can redistribute it and/or modify             #
#     it under the terms of the GNU General Public License as published by      #
#     the Free Software Foundation, either version 3 of the License, or         #
#     (at your option) any later version.                                       #
#                                                                               #
#     IASIC is distributed in the hope that it will be useful,                  #
#     but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#     GNU General Public License for more details.                              #
#                                                                               #
#     You should have received a copy of the GNU General Public License         #
#     along with Foobar.  If not, see <https://www.gnu.org/licenses/>.          #
#                                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Package:      IASIC
# File:         db/install.sql
# Author:       Erich Kohmann (erich.kohmann@gmail.com)
# Description:  This is the queries-script to be ran only once when you're configuring the sql-database


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
