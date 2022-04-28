import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Appointment:
    def __init__(self, A_ID, time, caregiver, patient, vaccine):
        self.A_ID = A_ID
        self.time = time
        self.patient = patient
        self.caregiver = caregiver
        self.vaccine = vaccine

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_appointment_details = "SELECT * FROM Appointments WHERE Appointment_ID = %s"
        try:
            cursor.execute(get_appointment_details, self.time)
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

    def get_A_ID(self):
        return self.A_ID

    def get_date(self):
        return self.date

    def get_patient(self):
        return self.patient
    
    def get_caregiver(self):
        return self.caregiver

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_Appointment = "INSERT INTO Appointments VALUES (%s, %s, %s, %s, %s)"
        try:
            cursor.execute(add_Appointment, (self.A_ID, self.time, self.caregiver, self.patient, self.vaccine))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()