from functools import partial

import mysql.connector
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivymd import app
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.theming import ThemeManager
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string
import random


from Opening_Screens_1.signup_methods import signup, finish_signup, send_verification_email, \
                                              verify_and_create_user, resend_verification_code
from Opening_Screens_1.login_methods import login, finish_login, login_attempt
from Landing_Screen_2.landing_screen_methods import get_quote


#This class manages the screen.
class MainScreen(MDScreen):
    pass

# THE MAIN APP CLASS
class YourApp(MDApp):
    # -----------------------------------------------------------------------------------------------
    # Universal/Initiation Methods --------------------------
    # -----------------------------------------------------------------------------------------------
    def change_screen(self):
        self.root.clear_widgets()
        self.root.add_widget(self.screen)

    def on_start(self):
        # Connect to MySQL database on app start
        self.mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Sinabina1334!",
            database="wellness_app_db"
        )
        self.mycursor = self.mydb.cursor()
        # Variables for signup/login process
        self.vf_code = None
        self.userfirstName = None
        self.userlastName = None
        self.userEmail = None
        self.userPassword = None
        self.createUserTask = None
        self.user_uid = None
        # After login User Data Variables
        self.standard_fitness_templates = []
        self.user_custom_fitness_templates = []

    def build(self):
        self.theme_cls.primary_palette = 'Teal'
        self.theme_cls.primary_hue = '500'
        self.theme_cls.theme_style = 'Light'
        self.screen = Builder.load_file('Opening_Screens_1/1_opening_screen.kv')
        return self.screen

    def get_user_data(self):
        # get all fitness standard templates
        sql_statement = "SELECT * FROM workout_template_header"
        self.mycursor.execute(sql_statement)
        results = self.mycursor.fetchall()
        for result in results:
            self.standard_fitness_templates.append(result)
        # get all fitness user custom templates
        sql_statement = "SELECT * FROM user_workout_header WHERE user_uid = {}".format(self.user_uid)
        self.mycursor.execute(sql_statement)
        results = self.mycursor.fetchall()
        for result in results:
            self.user_custom_fitness_templates.append(result)


    #----------------------------
    #-- NAVIGATION BAR METHODS --
    # ----------------------------
    def menu_home(self):
        self.screen = Builder.load_file('Landing_Screen_2/5_landing_screen.kv')
        self.change_screen()

    def menu_fitness(self):
        sql_statement = "SELECT * FROM user_workout_header WHERE user_uid = {} AND is_complete = 'N' AND is_delete = 'N'".format(self.user_uid)
        self.mycursor.execute(sql_statement)
        results = self.mycursor.fetchall()
        # if there is no current workout program, get screen to start new program
        if len(results) == 0:
            self.screen = Builder.load_file('Fitness_Screens_3/6_fitness_screen_new.kv')
            self.display_standard_fitness_templates()
            self.display_user_custom_fitness_templates()
            self.display_user_custom_workout_history()
            self.change_screen()
        # if there is a current workout program, show next workout in program
        else:
            self.screen = Builder.load_file('Fitness_Screens_3/6_fitness_screen_workout.kv')
            self.change_screen()

    def menu_nutrition(self):
        pass

    def menu_enneagram(self):
        pass

    def menu_settings(self):
        pass

    def menu_logout(self):
        # also need to clear cache for login info
        self.screen = Builder.load_file('Opening_Screens_1/1_opening_screen.kv')
        self.change_screen()

    # -----------------------------------------------------------------------------------------------
    # Signup/Verification Screens Methods -------------------
    # (see "signup_methods.py" in the "Opening_Screens" folder for logic)
    # -----------------------------------------------------------------------------------------------
    def signup(self):
        signup(self)

    def finish_signup(self, first_name, last_name, email, password, re_password):
        finish_signup(self, first_name, last_name, email, password, re_password)

    def send_verification_email(self):
        send_verification_email(self)

    def verify_and_create_user(self): #--main one, takes to landing screen
        verify_and_create_user(self)
        self.get_user_data()

    def resend_verification_code(self):
        resend_verification_code(self)

    # -----------------------------------------------------------------------------------------------
    # Login Screen Methods ----------------------------------
    # (see "login_methods.py" in the "Opening_Screens" folder for logic)
    # -----------------------------------------------------------------------------------------------
    def login(self):
        login(self)

    def finish_login(self, email, password):
        finish_login(self, email, password)

    def login_attempt(self, result, real_password, attempts_left, email, password):
        login_attempt(self, result, real_password, attempts_left, email, password)
        self.get_user_data()

    # -----------------------------------------------------------------------------------------------
    # Landing Screen Methods ----------------------------------
    # (see "landing_screen_methods.py" in the "Opening_Screens" folder for logic)
    # -----------------------------------------------------------------------------------------------
    def get_quote(self):
        quote = get_quote(self)
        return quote

    # -----------------------------------------------------------------------------------------------
    # Fitness Screens Methods ----------------------------------
    # (see "landing_screen_methods.py" in the "Opening_Screens" folder for logic)
    # -----------------------------------------------------------------------------------------------
    def get_current_workout_program(self):
        sql_statement = "SELECT * FROM user_workout_header WHERE is_complete = 'N' AND is_delete = 'N'"
        self.mycursor.execute(sql_statement)
        result = self.mycursor.fetchall()



    def display_standard_fitness_templates(self):
        for i in range(10):
            name = "Program " + str(i)
            card = MDCard(id=name,
                          size_hint = (None, None),
                          orientation = "vertical",
                          size = ("75dp", "150dp"),
                          elevation = 2,
                          radius = [20, ],
                          on_release = partial(self.on_card_click, name),  #even though I am trying to pass a variable, it is passing the card object itself instead.
                          md_bg_color = (59 / 255, 209 / 255, 199 / 255, 1)  # light Teal color
                        )
            label = MDLabel(text=name, theme_text_color="Custom",
                            text_color=(94/255,104/255,112/255,1),  # dark grey
                            font_style="Body1")
            card.add_widget(label)
            #card_pos = (i * (card.width + dp(15)), 0)
            #card.pos_hint = {"x": None, "y": None}
            #card.pos = card_pos
            self.screen.ids.std_templates_container.add_widget(card)

    def on_card_click(self, card_object):
        template_name = card_object.id
        print("Hello, ", template_name)

        '''
        for template in self.standard_fitness_templates:
            card = MDCard(size_hint = (None, None),
                            size = (Window.width, "75dp"),
                            pos_hint = {"center_x": .5},
                            elevation = 2,
                            padding = "8dp",
                            spacing = "15dp",
                            radius = [15,],
                            md_bg_color = (94/255, 104/255, 112/255, 1)) #dark grey
            #card_layout = BoxLayout(orientation="vertical", padding="8dp", spacing="8dp")
            label = MDLabel(text=template[1], theme_text_color="Custom",
                            text_color=(59/255, 209/255, 199/255, 1), #light teal
                            font_style="Body1")
        '''
        '''
            sexCard = MDCard(size_hint = (None, None),
                            size = ("20db", "10dp"),
                            pos_hint = {"center_x": .5},
                            elevation = 2,
                            padding = "8dp",
                            spacing = "15dp",
                            radius = [15,],
                            md_bg_color = (94/255, 104/255, 112/255, 1))
        '''
        '''
            #card_layout.add_widget(label)
            #card.add_widget(card_layout)
            card.add_widget(label)
            self.screen.ids.standard_fitness_templates_display.add_widget(card)
        # Bind the card's width to the window's width
        Window.bind(width=self.update_card_width)
        '''

    def update_card_width(self, instance, width):
        for widget in self.screen.ids.standard_fitness_templates_display.children:
            if isinstance(widget, MDCard):
                widget.width = width

    def display_user_custom_fitness_templates(self):
        for template in self.user_custom_fitness_templates:
            label = MDLabel(text=template[1], theme_text_color="Custom",
                            text_color=(46/255, 140/255, 134/255, 1), #dark teal
                            font_style="Body1")
            self.screen.ids.user_custom_fitness_templates_display.add_widget(label)

    def display_user_custom_workout_history(self):
        pass






# Run the app
if __name__ == '__main__':
    YourApp().run()


