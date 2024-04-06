
from kivy.lang import Builder
from datetime import datetime


def login(self):
    self.screen = Builder.load_file('Opening_Screens_1/3_login_screen.kv')
    self.change_screen()


def finish_login(self, email, password):
    # if the user does not enter information, give an error message
    if email == '' or password == '':
        self.screen.ids.login_error_label.text = "** Please enter an Email and Password **"
    # otherwise
    else:
        sql_statement = "SELECT * FROM users WHERE email_address = '{}'".format(email)
        self.mycursor.execute(sql_statement)
        result = self.mycursor.fetchall()
        # if the email/user exists in the DB
        if len(result) > 0:
            delete_flag = result[0][12]
            if delete_flag == 'N':
                real_password = result[0][4]
                attempts_left = result[0][13]
                # if you still have login attempts remaining
                if attempts_left > 0:
                    self.login_attempt(result, real_password, attempts_left, email, password)
                # otherwise must wait 15 minutes before login can be re-attempted
                else:
                    last_attempt_time = result[0][14]
                    current_datetime = datetime.now()
                    difference = int((current_datetime - last_attempt_time).total_seconds() / 60)
                    minutes_remaining = 15 - difference
                    # if there is still time remaining before next attempt, show error message
                    if minutes_remaining > 0:
                        self.screen.ids.login_error_label.text = str(
                            "** Must wait {} minutes before you can re-attempt login **".format(minutes_remaining))
                    # otherwise set attempts back to 3 and re-attempt login
                    else:
                        update_statement = "UPDATE users \
                                            SET \
                                                login_attempts_remaining = 3 \
                                            WHERE email_address = '{}'".format(email)
                        self.mycursor.execute(update_statement)
                        self.mydb.commit()
                        self.login_attempt(result, real_password, attempts_left, email, password)
            # if entered email belongs to a "deleted" account
            else:
                self.screen.ids.login_error_label.text = "** This account is deleted. Please go through the signup process to re-activate **"
        # if the email/user does NOT exist in the DB
        else:
            self.screen.ids.login_error_label.text = "** User Does Not Exist **"


def login_attempt(self, result, real_password, attempts_left, email, password):
    if attempts_left > 0:
        if password == real_password:
            # print('CORRECT! LOGIN SUCCESS! Hello {}'.format(result[0][2] + ' ' + result[0][3]))
            update_statement = "UPDATE users \
                                SET \
                                    login_attempts_remaining = 3, \
                                    last_login_attempt = NOW(), \
                                    last_login_successful = NOW() \
                                WHERE email_address = '{}'".format(email)
            self.mycursor.execute(update_statement)
            self.mydb.commit()
            self.user_uid = result[0][0]
            self.screen = Builder.load_file('Landing_Screen_2/5_landing_screen.kv')
            self.change_screen()
        else:
            attempts_left = attempts_left - 1
            update_statement = "UPDATE users \
                                SET \
                                    login_attempts_remaining = {}, \
                                    last_login_attempt = NOW() \
                                WHERE email_address = '{}'".format(attempts_left, email)
            self.mycursor.execute(update_statement)
            self.mydb.commit()
            if attempts_left == 0:
                self.screen.ids.login_error_label.text = str(
                    "** Must wait 15 minutes before you can re-attempt login **".format(attempts_left))
            else:
                self.screen.ids.login_error_label.text = str(
                    "** Incorrect Password, {} attempts remaining **".format(attempts_left))