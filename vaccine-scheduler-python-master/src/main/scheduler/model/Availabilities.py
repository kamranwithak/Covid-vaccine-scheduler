import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql


class Availabilities:
    def __init__(self, time):
        self.time = time

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        available_caregivers = ""

        get_availability_details = "SELECT Username FROM Availabilities WHERE Time = %s"
        try:
            cursor.execute(get_availability_details, self.time)
            for row in cursor:
                curr_username = row['Username'] 
                available_caregivers = available_caregivers + curr_username + " "
            cm.close_connection()
            return available_caregivers
        except pymssql.Error as e:
            print("Error occurred when fetching current availabilities")
            raise e
        finally:
            cm.close_connection()

    def get_time(self):
        return self.time
    
    def random_caregiver(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        curr_username = ""

        get_random_caregiver = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY NEWID()"
        try:
            cursor.execute(get_random_caregiver, self.time)
            for row in cursor:
                curr_username = row['Username']
            cm.close_connection()
            return str(curr_username)
        except pymssql.Error as e:
            print("Error occurred when fetching current availabilities")
            raise e
        finally:
            cm.close_connection()