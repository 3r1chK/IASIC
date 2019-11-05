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
#     along with IASIC.  If not, see <https://www.gnu.org/licenses/>.          #
#                                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Package:      IASIC
# File:         classes/DbInterface.py
# Author:       Erich Kohmann (erich.kohmann@gmail.com)
# Description:  This class works as interface between IASIC and the sql-database


import mysql.connector
from mysql.connector import errorcode


class DbInterface:

    configs = {}
    cnx = None
    db_config_path = "./config/db.txt"

    def __init__(self, log_handler):
        self.readConfig()
        self.log_handler = log_handler

    def connect(self):
        if self.cnx is not None:
            self.cnx.close()
        # Create a new mysql-connection and store its descriptor as Class Attribute
        try:
            self.cnx = mysql.connector.connect(**self.configs)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.log_handler.print("Something is wrong with your user name or password", 0)
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self.log_handler.print("Database does not exist", 0)
            else:
                self.log_handler.print(str(err), 0)
            return False

        if self.cnx is not None:
            #self.cnx.autocommit = True   # Enable auto-commit!
            return True
        return False

    def storePredictions(self, predictions):
        self.connect()
        query = "SELECT max(prediction_id) FROM marine_classification.predictions;"
        cursor = self.cnx.cursor()
        cursor.execute(query)
        res = cursor.fetchone()
        prediction_id = 0
        if res[0] is not None:
            prediction_id = int(res[0])+1

        for prediction in predictions:
            q = "INSERT INTO marine_classification.predictions (prediction_id, class_index, predicted_class, probability) VALUES (%s, %s, %s, %s);"
            cursor.execute(q, (prediction_id, prediction[0], prediction[1], str(prediction[2])))

        cursor.close()
        self.cnx.commit()
        return prediction_id

    def storeImageEntry(self, db_entry):
        self.connect()
        query = "INSERT INTO `marine_classification`.`images` "\
                "(`predictions_id`, `location_id`, `status`, " \
                "`insta_url`, `local_uri`, `sha256_digest`) VALUES ( %s, %s, %s, %s, %s, %s);"
        params = (
            db_entry['prediction_id'],
            db_entry['location_id'],
            db_entry['status'],
            db_entry['insta_url'],
            db_entry['uri'],
            db_entry['sha256_digest']
        )
        cursor = self.cnx.cursor()
        cursor.execute(query, params)
        res = True
        if cursor.rowcount < 1:
            res = False
        cursor.close()
        self.cnx.commit()
        return res

    def storeLocation(self, location):
        if location is None:
            return 0
        # Look for such a location in the db, if it doesn't exists create a new one and update db_entry location id
        r = self.locationAlreadyExists(location)

        if r == 0:
            # Create a new location entry into the db and return it ID
            self.connect()
            q = "INSERT INTO `marine_classification`.`locations`" \
                "(`name`,`latitude`,`longitude`) VALUES ( %s, %s, %s );"
            p = (location["name"], location["lat"], location["lng"])
            cursor = self.cnx.cursor()
            cursor.execute(q, p)
            if cursor.rowcount > 0:
                r = self.locationAlreadyExists(location)
            cursor.close()
            self.cnx.commit()

        return r

    def locationAlreadyExists(self, location):
        if location is None:
            return 0
        self.connect()
        q = "SELECT `_id` FROM `marine_classification`.`locations` WHERE name='"+str(location["name"])+"' AND " \
                                                                         "latitude='"+str(location["lat"])+"' AND" \
                                                                         "longitude='"+str(location["lng"])+"';"
        cursor = self.cnx.cursor()
        cursor.execute(q)
        r = cursor.fetchall()
        cursor.close()
        self.cnx.commit()
        if r is None or len(r) == 0:
            return 0
        return r[0][0]

    def instaUrlAlreadyExists(self, insta_url):
        self.connect()
        q = "SELECT `_id`,`insta_url` FROM `marine_classification`.`images` WHERE insta_url='"+str(insta_url)+"';"
        cursor = self.cnx.cursor()
        cursor.execute(q)
        r = cursor.fetchall()
        cursor.close()
        self.cnx.commit()
        if r is None or len(r) == 0:
            return False
        if str(r[0][1]) != insta_url:
            return False
        self.log_handler.write("## DbInterface.instaUrlAlreadyExists("+insta_url+") = True 'case of ("+str(r[0][0])+", "+str(r[0][1])+")", 3)
        return True

    def fileAlreadyExists(self, checksum):
        self.connect()
        q = "SELECT `_id`,`sha256_digest` FROM `marine_classification`.`images` WHERE sha256_digest='"+str(checksum)+"';"
        cursor = self.cnx.cursor()
        cursor.execute(q)
        r = cursor.fetchall()
        self.cnx.commit()
        cursor.close()
        if r is None or len(r) == 0:
            return False
        if str(r[0][1]) != checksum:
            return False
        self.log_handler.write("## DbInterface.fileAlreadyExists("+checksum+") = True 'case of ("+str(r[0][0])+", "+str(r[0][1])+")", 3)
        return True

    def readConfig(self):
        # Read mysql-connection configs and re-arrange them
        rd = open(self.db_config_path, "r")
        self.configs = rd.readlines()
        rd.close()
        for i in range(len(self.configs)):
            if self.configs[i][-1:] == "\n":
                self.configs[i] = self.configs[i][:-1]
        self.configs = {
          'user': self.configs[1],
          'password': self.configs[2],
          'host': self.configs[0],
          'database': self.configs[4],
          'raise_on_warnings': True
        }

    def __del__(self):
        if self.cnx is not None:
            self.cnx.close()
