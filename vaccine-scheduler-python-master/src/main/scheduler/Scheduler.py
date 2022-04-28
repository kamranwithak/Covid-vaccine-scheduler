from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Availabilities import Availabilities
from model.Appointments import Appointment
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import random


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Create patient failed, Cannot save")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
        return
    print(" *** Account created successfully *** ")

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
    finally:
        cm.close_connection()
    return False
    

def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]
    
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Create caregiver failed, Cannot save")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
        return
    print(" *** Account created successfully *** ")


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("You need to enter a password and a username, but nothing else. Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login patient failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when logging in. Please try again!")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Error occurred when logging in. Please try again!")
    else:
        print("Patient logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("You need to enter a password and a username, but nothing else. Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login caregiver failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when logging in. Please try again!")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Error occurred when logging in. Please try again!")
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    # search_caregiver_schedule <date>
    # check 1: see if someone's logged in
    global current_caregiver
    global current_patient
    
    if current_caregiver is None and current_patient is None:
        print("Please login as a patient or a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return
    
    date = tokens[1]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)
    
    # check 3: checking if there are any availabilities for the give date
    if not search_schedule_exists(d):
        print("There are no availabilities for this date.")
        return
    
    usernames = None
    try:
        usernames = Availabilities(d).get()
    except pymssql.Error as e:
        print("Search for caregiver schedules failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when searching for caregiver schedules. Please try again!")
        print("Error:", e)
        return

    # check if the schedule search was successful
    if usernames is None:
        print("Error occurred when searching for caregiver schedules. Please try again!")
    else:
        print("The caregivers available for the date: " + date + ", are: " + usernames)
        display_vaccines()


def search_schedule_exists(date):
    cm = ConnectionManager()
    conn = cm.create_connection()
    
    select_date = "SELECT * FROM Availabilities WHERE Time = %s"

    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_date, date)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Time'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking schedules.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def display_vaccines():
    cm = ConnectionManager()
    conn = cm.create_connection()
    
    select_vaccine = "SELECT * FROM Vaccines"

    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_vaccine)
        for row in cursor:
            print("Vaccine:", row['Name'], " Doses:", row['Doses'])
    except pymssql.Error as e:
        print("Error occurred when looking for available Vaccines")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
    finally:
        cm.close_connection()
    return

def reserve(tokens):
    # reserve <date> <vaccine>
    # check 1: check if the current logged-in user is a patient
    global current_patient
    if current_patient is None:
        print("Please login as a patient first!")
        return
    
    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("You must only enter a date and a single vaccine. Please try again!")
        return

    date = tokens[1]
    vaccine = tokens[2]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)
    
    # check 3: check if there are any availabilities that day
    if not search_schedule_exists(d):
        print("There are no availabilities for this date.")
        return
    
    # check 4: check if the requested vaccine is real 
    if not vaccine_exists(vaccine):
        print("The vaccine you requested is not one that we carry. Please try another!")
        return

    reserve = None
    caregiver = Availabilities(time=d).random_caregiver()
    A_ID = int(random.uniform(999999, 100000))
    patient = current_patient.get_username()

    # reserve the appointment
    reserve = Appointment(A_ID=A_ID, time=d, caregiver=caregiver, patient=patient, vaccine=vaccine)

    # save the appointment to our database
    try:
        reserve.save_to_db()
    except pymssql.Error as e:
        print("Reservation failed, Cannot save")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
        return
    #remove our caregiver from availability table.
    Caregiver(username=caregiver).remove_availability(d)
    print(" *** Your reservation has been made *** ")
    print("Your assigned caregiver will be", caregiver)
    print("Your Appointment ID is:", A_ID)

def vaccine_exists(name):
    cm = ConnectionManager()
    conn = cm.create_connection()
    
    select_name = "SELECT * FROM Vaccines WHERE Name = %s"

    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_name, name)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Name'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking our vaccine records.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Failed to get Vaccine information")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to get Vaccine information")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Failed to add new Vaccine to database")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Failed to add new Vaccine to database")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Failed to increase available doses for Vaccine")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Failed to increase available doses for Vaccine")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):

    if len(tokens) != 1:
        print("Please try again!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    
    global current_caregiver
    global current_patient
    
    if current_patient is None and current_caregiver is None:
        print("Please log in as either a patient or a caregiver first!")
        return
    
    if current_patient is not None:
        print("Your appointments are:")
        patient_username = current_patient.get_username()
        select_appointments = "SELECT Appointment_ID, Vaccine, Time, Caregiver FROM Appointments WHERE Patient = %s"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(select_appointments, patient_username)
            for row in cursor:
                print("Appointment_ID:", row['Appointment_ID'], " Vaccine:", row['Vaccine'], "Date:", row['Time'], "Caregiver", row['Caregiver'])
        except pymssql.Error as e:
            print("Error occurred when looking for available appointments.")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error:", e)
        finally:
            cm.close_connection()
            return
        
    if current_caregiver is not None:
        print("Your appointments are")
        caregiver_username = current_caregiver.get_username()
        select_appointments = "SELECT Appointment_ID, Vaccine, Time, Patient FROM Appointments WHERE Caregiver = %s"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(select_appointments, caregiver_username)
            for row in cursor:
                print("Appointment_ID:", row['Appointment_ID'], " Vaccine:", row['Vaccine'], "Date:", row['Time'], "Patient", row['Patient'])
        except pymssql.Error as e:
            print("Error occurred when looking for available appointments.")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error:", e)
        finally:
            cm.close_connection()
            return



def logout(tokens):
    #  check 1: check if the current user is logged in
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("You are not logged in yet!")
        return
    
    #  check 2: let the user know how logout works
    if len(tokens) > 1:
        print("There is no need to enter anything to log out.")
    
    caregiver = None
    current_caregiver = caregiver
    patient = None
    current_patient = patient

    # set the current_caregiver and current_patient as None and let the user know they have logged out
    if current_caregiver is None and current_patient is None:
        print("Succesfully logged out!")
        return

def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  #// TODO: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  #// TODO: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine>") #// TODO: implement reserve (Part 2)
        print("> upload_availability <date>")
        print("> cancel <appointment_id>") #// TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  #// TODO: implement show_appointments (Part 2)
        print("> logout") #// TODO: implement logout (Part 2)
        print("> Quit")
        print()
        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Invalid Argument")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
