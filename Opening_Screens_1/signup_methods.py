import mysql.connector
from kivy.lang import Builder
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string
import random



def signup(self):
    self.screen = Builder.load_file('Opening_Screens_1/2_signup_screen.kv')
    self.change_screen()

# this method creates a new user, or updates the user if it exists and is set to "delete",
# or gives an error message if the user already exists and is active.
def finish_signup(self, first_name, last_name, email, password, re_password):
    # First check to make sure the passwords match before moving forward
    if password == re_password:
        # Next check to see if the email already exists in the database (can only have 1)
        sql_statement = "SELECT * FROM users WHERE email_address = '{}'".format(email)
        self.mycursor.execute(sql_statement)
        result = self.mycursor.fetchall()
        if len(result) == 0:
            self.createUserTask = 'Insert'
            self.userfirstName = first_name
            self.userlastName = last_name
            self.userEmail = email
            self.userPassword = password
            self.vf_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.send_verification_email()
            self.screen = Builder.load_file('Opening_Screens_1/4_email_verification_screen.kv')
            self.change_screen()
        else:
            # if the email DOES exist in DB, attempt to update the user IF the user is currently set to "delete"
            if result[0][12] == 'Y':
                self.createUserTask = 'Update'
                self.userfirstName = first_name
                self.userlastName = last_name
                self.userEmail = email
                self.userPassword = password
                self.vf_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                self.send_verification_email()
                self.screen = Builder.load_file('Opening_Screens_1/4_email_verification_screen.kv')
                self.change_screen()
            # if the email DOES exist in DB, and it is not set to "delete" give error message
            else:
                self.screen.ids.signup_error_label.text = "** Active Email Already Exists **"
    else:
        self.screen.ids.signup_error_label.text = "** Passwords Do Not Match **"


def send_verification_email(self):
    # Email Server Variables
    sender_email = "34ashurtz@gmail.com"
    sender_password = "hmbt kbqy rgyr fgwj"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    # Message configuration
    message = MIMEMultipart()
    message["From"] = "34ashurtz@gmail.com"
    message["To"] = self.userEmail
    message["Subject"] = "Wellness App Verification Code"
    body = "Hello {}, thank you joining the Wellness App! To complete your singup, use this verification code: {}".format(
        self.userfirstName, self.vf_code)
    message.attach(MIMEText(body, "plain"))
    # Connect to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)  # (smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)  # (sender_email, sender_password)
    # Send the email
    server.sendmail(sender_email, self.userEmail, message.as_string())
    # Disconnect from the server
    server.quit()


def verify_and_create_user(self):
    # if they entered the correct verification code
    if self.screen.ids.verification_code_field.text == self.vf_code:
        # print("Correct!!")
        # if the user does not exist, insert the new user
        if self.createUserTask == 'Insert':
            try:
                sql_statement = "INSERT INTO users (email_address, first_name, last_name, password, email_verified)\
                                VALUES (%s, %s, %s, %s, %s)"
                val = (self.userEmail, self.userfirstName, self.userlastName, self.userPassword, 'Y')
                self.mycursor.execute(sql_statement, val)
                self.mydb.commit()
                sql_statement = "SELECT * FROM users WHERE email_address = '{}'".format(self.userEmail)
                self.mycursor.execute(sql_statement)
                result = self.mycursor.fetchall()
                self.user_uid = result[0][0]
                self.screen = Builder.load_file('Landing_Screen_2/5_landing_screen.kv')
                self.change_screen()
            except mysql.connector.Error as err:
                self.screen.ids.verification_label.theme_text_color = 'Error'
                self.screen.ids.verification_label.text = str(
                    "There was an error trying to create your account. Error: {}".format(err))
        # if the user does exist and the account is set to "delete", update the account
        elif self.createUserTask == 'Update':
            try:
                sql_statement = "Update users \
                                 SET \
                                    first_name = '{}', \
                                    last_name = '{}', \
                                    password = '{}', \
                                    email_verified = 'Y', \
                                    delete_flag = 'N' \
                                 WHERE email_address = '{}'".format(self.userfirstName, self.userlastName,
                                                                    self.userPassword, self.userEmail)
                self.mycursor.execute(sql_statement)
                self.mydb.commit()
                self.screen = Builder.load_file('Landing_Screen_2/5_landing_screen.kv')
                self.change_screen()
            except mysql.connector.Error as err:
                self.screen.ids.verification_label.theme_text_color = 'Error'
                self.screen.ids.verification_label.text = str(
                    "There was an error trying to create your account. Error: {}".format(err))
        # if self.createUserTask is still "None"
        else:
            self.screen.ids.verification_label.theme_text_color = 'Error'
            self.screen.ids.verification_label.text = "There was an error trying to create your account, Do not know how to create user"
    # if they entered the incorrect verification code
    else:
        self.screen.ids.verification_label.theme_text_color = 'Error'
        self.screen.ids.verification_label.text = "Incorrect Verification Code"


def resend_verification_code(self):
    self.send_verification_email()
    self.screen.ids.verification_label.text_color = (46 / 255, 140 / 255, 134 / 255, 1)
    self.screen.ids.verification_label.text = "Email has been re-sent with a verification code, this may take several minutes to reach you"
