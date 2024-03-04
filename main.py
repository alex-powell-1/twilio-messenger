from os import environ
import tkinter
# Set to disable console output upon initialization
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import ttkbootstrap as ttk
from tkinter import messagebox, PhotoImage, scrolledtext
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import Querybox
import pandas
from sys import platform
from twilio.rest import Client
import pyodbc
import pygame
from pygame import mixer
from datetime import datetime
from dateutil import tz
import json
import sys
import ntplib
from ntplib import NTPException
import random
import creds
import theme


r"""
 ___  __  __  ___    __  __  ____  ___  ___  ____  _  _  ___  ____  ____ 
/ __)(  \/  )/ __)  (  \/  )( ___)/ __)/ __)( ___)( \( )/ __)( ___)(  _ \
\__ \ )    ( \__ \   )    (  )__) \__ \\__ \ )__)  )  (( (_-. )__)  )   /
(___/(_/\/\_)(___/  (_/\/\_)(____)(___/(___/(____)(_)\_)\___/(____)(_)\_)

Authored by: Alex Powell
December 15, 2023
Version: 1
"""

# Timezone
UTC_TIME = tz.gettz('UTC')
EST_TIME = tz.gettz('America/New_York')

# Text Sounds
# In try block in case system does not have a sound card and cannot initialize mixer
try:
    mixer.init()
except pygame.base.error:
    sound = False
else:
    sound = True
    customer_sound = mixer.Sound("./sounds/chime.wav")
    store_sound = mixer.Sound("./sounds/pop.wav")

# Database
SERVER = creds.SERVER
DATABASE = creds.DATABASE
USERNAME = creds.USERNAME
PASSWORD = creds.PASSWORD

# Twilio
TWILIO_PHONE_NUMBER = creds.TWILIO_PHONE_NUMBER
account_sid = creds.account_sid
auth_token = creds.auth_token

# Global Variables
recent_messages = ""
most_recent_message = {}
userid = ""
user = ""

# Images
application_icon = "./images/icon.png"
application_logo = "./images/logo_small.png"


# -------------------- USER INTERFACE --------------------- #
# Create the main window
class LoginWindow:
    def __init__(self):
        self.parent = ttk.Window()
        style = ttk.Style()
        style.configure('my.TButton', font=(theme.main_font, 11), background=theme.login_button_color, padding=10)
        self.style = ttk.Style()
        self.style.configure('my.TButton', font=(theme.main_font, 11), background=theme.login_button_color, padding=10)
        self.frame = ttk.Frame(self.parent)
        self.parent.tk.call('wm', 'iconphoto', self.parent._w, PhotoImage(file=application_icon))
        self.parent.title(theme.login_title)
        self.screen_width = self.parent.winfo_screenwidth()
        self.screen_height = self.parent.winfo_screenheight()
        self.parent.geometry(f"{round(self.screen_width * .25)}x{round(self.screen_height * .8)}")
        self.parent.position_center()
        self.parent.tk.call('wm', 'iconphoto', self.parent._w, PhotoImage(file=application_icon))
        self.logo = ttk.PhotoImage(file=application_logo)
        self.logo_label = ttk.Label(self.frame, image=self.logo)
        self.logo_label.pack(side="top")
        # Create and place the username label and entry
        self.username_label = ttk.Label(self.frame, text="Username:", justify="center", font=theme.login_label_font)
        self.username_label.pack(pady=5)
        self.username_entry = ttk.Entry(self.frame, justify="center", font=theme.login_label_font)
        self.username_entry.pack(pady=5)
        self.username_entry.focus_set()
        # Create and place the password label and entry
        self.password_label = ttk.Label(self.frame, text="Password:", justify="center", font=theme.login_label_font)
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self.frame, show="*", justify="center", font=theme.login_label_font)
        self.password_entry.pack(pady=5)
        self.password_entry.bind('<Return>', self.submit_form)
        # Create and place the login button
        self.login_button = ttk.Button(self.frame, text="Login", command=self.validate_login, style='my.TButton')
        self.login_button.pack(pady=15)
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.frame.pack(expand=True)
        # Start the Tkinter event loop
        self.parent.mainloop()

    def validate_login(self):
        global userid
        global user
        userid = self.username_entry.get()
        password = self.password_entry.get()

        try:
            if platform == "win32":
                file = open(creds.windows_user_path)
            else:
                file = open(creds.mac_user_path)
        except FileNotFoundError:
            if platform == "win32":
                messagebox.showerror("Login Failed", "Network error:\n\nCannot find user file.")
            else:
                messagebox.showerror("Login Failed", "Network error:\n\nCannot find user file.\n\n"
                                                     "Connect to share and try again.")
        else:
            data = json.load(file)

        for k, v in data.items():
            if k == userid and v['key'] == password:
                messagebox.showinfo("Login Successful", f"Welcome, {v['name']}!")
                # Destroy first window
                self.parent.destroy()
                # reset style
                ttk.Style.instance = None
                user = v['full_name']
                return
        else:
            messagebox.showerror("Login Failed", "Contact Administrator.")
            self.parent.focus()
            self.password_entry.focus_set()
            return

    def submit_form(self, event):
        self.validate_login()
        return

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.parent.destroy()
            sys.exit()
        else:
            self.password_entry.focus_set()

class MessengerWindow:
    def __init__(self):
        self.run_process = True
        self.app = ttk.Window(title=theme.messenger_title, themename='cosmo')
        style = ttk.Style()
        style.configure('my.TButton', font=(theme.main_font, 11), background=theme.login_button_color, padding=10)
        self.style = ttk.Style()

        self.screen_width = self.app.winfo_screenwidth()
        self.screen_height = self.app.winfo_screenheight()
        self.app.geometry(f"{round(self.screen_width * .25)}x{round(self.screen_height * .8)}")
        self.app.position_center()
        self.app.update()

        self.app.tk.call('wm', 'iconphoto', self.app._w, PhotoImage(file=application_icon))
        self.logo = ttk.PhotoImage(file=application_logo)
        self.logo_label = ttk.Label(self.app, image=self.logo)
        self.logo_label.pack(side="top")

        self.b1 = ttk.Button(self.app, text='Search Messages', bootstyle=OUTLINE, command=self.search_messages)
        self.b1.pack(side=TOP, padx=5, pady=5)

        # View Recent Messages
        self.b2 = ttk.Button(self.app, text='Get Recent Messages', bootstyle=SUCCESS, command=self.get_recent_messages)
        self.b2.pack(padx=5, pady=5)

        self.st = tkinter.scrolledtext.ScrolledText(self.app, width=250, height=10)
        self.st.pack(fill=BOTH, expand=YES)

        # Entry: To Phone
        self.to_phone_label = ttk.Label(self.app, text="Send to:", font=(theme.main_font, 10, "normal"))
        self.to_phone_label.pack(pady=10)

        self.to_phone_box = ttk.Entry(self.app, width=17, font=(theme.main_font, 12, "normal"), justify="center")
        self.to_phone_box.bind("<Tab>", self.focus_next_widget)
        self.to_phone_box.pack(expand=NO)
        self.to_phone_box.focus_set()

        # Customer Look-up
        self.b3 = ttk.Button(self.app, text='Customer Lookup', bootstyle=OUTLINE, command=self.lookup_customer_data)
        self.b3.pack(padx=5, pady=10)

        self.message_box = ttk.Text(self.app, width=34, height=3, wrap="word", font=(theme.main_font, 12, "normal"), fg="black", pady=10,
                               padx=10)
        self.message_box.bind("<Tab>", self.focus_next_widget)
        self.message_box.pack(expand=NO)

        self.logout_button = ttk.Button(self.app, text='Log Out', command=self.logout, bootstyle=SUCCESS, padding=10)
        self.logout_button.pack(side=BOTTOM, padx=5, pady=5)

        self.username_label = ttk.Label(self.app, text=f"User: {user}", font=(theme.main_font, 10, "italic"), foreground="#333333")
        self.username_label.pack(side=BOTTOM, pady=5)

        self.b3 = ttk.Button(self.app, text='Send Message', command=self.send_text, bootstyle=SUCCESS, padding=10)
        self.b3.pack(side=BOTTOM, padx=50, pady=5)

        self.twilio_client()
        self.app.mainloop()

    def twilio_client(self):
        """Once a user authenticates, the app will get and print all recent messages and then check for new messages"""
        self.get_recent_messages()
        self.get_most_recent_message()

    def logout(self):
        self.run_process = False

    def get_recent_messages(self, number_to_retrieve=40):
        """retrieves recent messages from share drive, clears scrolled text box, prints messages"""
        sms_messages = self.combine_and_sort_sms_by_date()
        # Clear Screen
        self.clear_scrolling_text()
        # Print SMS Messages to Scrolled Text Widget
        self.print_sms_messages(sms_messages, number_to_retrieve)
        # Update global variable with data of most recent message
        global most_recent_message
        most_recent_message = sms_messages[-1]
        return

    def read_incoming_sms_from_share_drive(self):
        """Get all Incoming data from share drive"""
        if platform == "darwin":
            incoming_data = pandas.read_csv(creds.mac_incoming_log_path)
        elif platform == "win32":
            incoming_data = pandas.read_csv(creds.windows_incoming_log_path)
        incoming_text_records = incoming_data.to_dict("records")
        return incoming_text_records

    def read_outgoing_sms_from_share_drive(self):
        """Get all outgoing SMS data from share drive"""
        outgoing_text_records = []
        try:
            if platform == "darwin":
                outgoing_data = pandas.read_csv(creds.mac_outgoing_log_path)
            elif platform == "win32":
                outgoing_data = pandas.read_csv(creds.windows_outgoing_log_path)
        except FileNotFoundError:
            return outgoing_text_records
        outgoing_text_records = outgoing_data.to_dict("records")
        return outgoing_text_records

    def combine_and_sort_sms_by_date(self):
        # Get Lists
        incoming_sms = self.read_incoming_sms_from_share_drive()
        outgoing_sms = self.read_outgoing_sms_from_share_drive()
        y = 0
        for x in outgoing_sms:
            incoming_sms.append(outgoing_sms[y])
            y += 1
        combined_sms_list = incoming_sms
        # Sort Combined List
        combined_and_sorted_sms_list = sorted(combined_sms_list, key=lambda d: d['date'])
        return combined_and_sorted_sms_list

    def convert_utc_to_local_datetime(self, timestamp, from_zone=UTC_TIME, to_zone=EST_TIME):
        """For converting TWILIO API UTC timestamp to EST"""
        utc = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        local_datetime = utc.astimezone(to_zone)
        local_date = local_datetime.strftime("%m-%d-%Y")
        local_time = local_datetime.strftime("%I:%M %p")
        return local_date, local_time

    def reformat_date_and_time(self, timestamp):
        """For converting TWILIO API UTC timestamp to EST"""
        utc = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        local_date = utc.strftime("%m-%d-%Y")
        local_time = utc.strftime("%I:%M %p")
        return local_date, local_time

    def print_sms_messages(self, incoming_sms_messages, number_of_messages):
        # Combine incoming and outgoing messages into one list by date
        for line in incoming_sms_messages[(number_of_messages * -1):]:
            # Set scrolled text widget to read/write and font to black
            self.st.config(state="normal", foreground="black")
            # Get timestamp, name, and customer category from CSV
            timestamp = line['date']
            customer_name = line['name']
            # Convert timestamp to EST
            local_date, local_time = self.reformat_date_and_time(timestamp)
            # Reformat Phone Number for Counterpoint Use and easy user viewing
            formatted_from_phone = self.format_phone(line['from_phone'], mode="Counterpoint")
            formatted_to_phone = self.format_phone(line['to_phone'], mode="Counterpoint")
            # Update Screen
            self.app.update()
            # ------------------------INCOMING MESSAGES------------------------#
            if formatted_from_phone != self.format_phone(creds.TWILIO_PHONE_NUMBER, mode="Counterpoint"):
                customer_name = line['name']
                customer_category = line['category']
                media_url = line['media']
                color_tag = 'customer'
                # Insert Text
                self.st.insert(END, f" \n------------------------------------------------\n\n"
                               f" Date: {local_date} at Time: {local_time}\n From:", f"{color_tag}header")
                self.st.insert(END, f"{formatted_from_phone}\n", f"{color_tag}phone")
                self.st.insert(END, f" Name: {customer_name} Category: {customer_category}\n", f"{color_tag}header")
                self.st.insert(END, f" {line['body']}\n", f"{color_tag}message")
                if media_url != "No Media":
                    self.st.insert(END, f" Picture URL: \n{line['media']}\n", f"{color_tag}message")
                # ...with styling tags
                self.st.tag_config('customerheader', foreground="#333333", font=("Open Sans", 10, "italic"),
                              lmargin1=0, rmargin=10)
                self.st.tag_config('customerphone', foreground="#333333",
                              justify="left", font=("Open Sans", 10, "bold"), lmargin1=0, rmargin=10)
                self.st.tag_config('customermessage', foreground="black", font=(theme.main_font, 13, "normal"),
                              wrap="word", lmargin1=0, rmargin=10)
            else:
                # ------------------------OUTGOING MESSAGES------------------------#
                # Check if it is an outgoing message
                if formatted_from_phone == self.format_phone(creds.TWILIO_PHONE_NUMBER, mode="Counterpoint"):
                    user_id = line['user'].title()
                    color_tag = 'store'
                    self.st.insert(END, f" \n------------------------------------------------\n\n"
                                   f" Date: {local_date} at Time: {local_time}\n To: ", f"{color_tag}header")
                    self.st.insert(END, f"{customer_name} at {formatted_to_phone}\n", f"{color_tag}header")
                    self.st.insert(END, f" User: {user_id}\n", f"{color_tag}phone")
                    self.st.insert(END, f" {line['body']}\n", f"{color_tag}message")
                    # ...with styling tags
                    self.st.tag_config('storeheader', foreground="#333333", justify="left",
                                  font=theme.datetime_header_font,
                                  lmargin1=0, rmargin=10)
                    self.st.tag_config('storephone', foreground="#333333", justify="left", font=theme.phone_header_font,
                                  lmargin1=0, rmargin=10)
                    self.st.tag_config('storemessage', foreground="green", justify="left", font=theme.message_font,
                                  wrap="word", lmargin1=0, rmargin=10)

            # Automatically Scroll to end
            self.st.see(ttk.END)
            # Make Text Read Only
            self.st.config(state="disabled")

    def get_most_recent_message(self):
        """gets the timestamp for the most recent text message in csv file"""
        sms_messages = self.combine_and_sort_sms_by_date()
        global most_recent_message
        index_of_previous_most_recent = sms_messages.index(most_recent_message)
        messages_to_print = sms_messages[index_of_previous_most_recent + 1:]
        self.print_sms_messages(messages_to_print, len(messages_to_print))

        # Update most recent message
        if len(messages_to_print) > 0:
            # Play Sound Effect for each new message
            # Try block in case of missing audio driver
            if sound:
                for x in messages_to_print:
                    if x['from_phone'] == TWILIO_PHONE_NUMBER[2:]:
                        store_sound.play()
                    else:
                        customer_sound.play()
            # Update Most Recent Message Global Variable
            most_recent_message = messages_to_print[-1]

        # Wait, then loop process again
        if self.run_process:
            self.app.after(1000, self.get_most_recent_message)
        else:
            ttk.Style.instance = None
            self.app.destroy()
            application()

    # -------------Customer Lookup--------------- #

    def lookup_last_message_sent(self, phone_number):
        """Gets all messages from twilio API and writes to .csv on share drive"""
        client = Client(account_sid, auth_token)
        messages = client.messages.list(to=phone_number)
        # Empty List
        message_list = []
        for message in messages:
            message_list.append(message.body)
        return message_list[0]

    # ----------------------- LOOKUP CUSTOMER POPUP -------------------------#
    def lookup_customer_data(self):
        # Get user input from 'to' field
        user_phone_input = self.to_phone_box.get()
        # Look up last message sent via Twilio
        last_twilio_message = self.lookup_last_message_sent(self.format_phone(user_phone_input, prefix=True))
        # Format phone for Counterpoint masking ###-###-####
        cp_phone_input = self.format_phone(user_phone_input, mode="Counterpoint")
        # Create customer variables from tuple return of query_db
        try:
            customer_name, customer_email, rewards_points, last_sale_date, customer_category = self.query_db(cp_phone_input)
        # Create MessageBox with Customer Info
        except TypeError:
            messagebox.showinfo("Customer Info", "Customer Not Found")
        else:
            try:
                messagebox.showinfo("Customer Info", f"Name:\n{customer_name}\n\n"
                                                     f"Category:\n{customer_category}\n\n"
                                                     f"Email:\n{customer_email}\n\n"
                                                     f"Rewards Points:\n${rewards_points}\n\n"
                                                     f"Last Sale Date:\n{last_sale_date.strftime('%m/%d/%Y')}\n\n"
                                                     f"Last Twilio Message Sent:\n\n{last_twilio_message}")
            except AttributeError:
                messagebox.showinfo("Customer Info", f"Name:\n{customer_name}\n\n"
                                                     f"Email:\n{customer_email}\n\n"
                                                     f"Rewards Points:\n${rewards_points}\n\n"
                                                     f"Last Sale Date:\nNo Sales History\n\n"
                                                     f" Last Twilio Message Sent:\n\n{last_twilio_message}",
                                    icon="question")

    # ----------------------- GET CUSTOMER DATA FROM COUNTERPOINT -------------------------#
    def query_db(self, phone_number):
        customer_info = []
        connection = pyodbc.connect(
            f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};PORT=1433;DATABASE={DATABASE};'
            f'UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=yes;')
        cursor = connection.cursor()

        SQL_QUERY = f"""
                SELECT CUST_NO, FST_NAM, LST_NAM, PHONE_1, EMAIL_ADRS_1, LOY_PTS_BAL, LST_SAL_DAT, CATEG_COD
                FROM AR_CUST
                WHERE PHONE_1 = '{phone_number}' or PHONE_2 = '{phone_number}'
                """

        SQL = cursor.execute(SQL_QUERY).fetchall()
        cursor.close()
        # If there is a result, assign result to variables
        if SQL != []:
            customer_name = f"{SQL[0][1]} {SQL[0][2]}"
            customer_email = SQL[0][4]
            rewards_points = SQL[0][5]
            last_sale_date = SQL[0][6]
            customer_category = SQL[0][7]
            return customer_name, customer_email, rewards_points, last_sale_date, customer_category
        else:
            return "Unknown Name", "Unknown Email", 0, "No Sales History", "Unknown Category"

    # ----------------------- FORMAT PHONE NUMBERS -------------------------#
    def format_phone(self, phone_number, mode="Twilio", prefix=False):
        """Cleanses input data and returns masked phone for either Twilio or Counterpoint configuration"""
        phone_number_as_string = str(phone_number)
        # Strip away extra symbols
        formatted_phone = phone_number_as_string.replace(" ", "")  # Remove Spaces
        formatted_phone = formatted_phone.replace("-", "")  # Remove Hyphens
        formatted_phone = formatted_phone.replace("(", "")  # Remove Open Parenthesis
        formatted_phone = formatted_phone.replace(")", "")  # Remove Close Parenthesis
        formatted_phone = formatted_phone.replace("+1", "")  # Remove +1
        formatted_phone = formatted_phone[-10:]  # Get last 10 characters
        if mode == "Counterpoint":
            # Masking ###-###-####
            cp_phone = formatted_phone[0:3] + "-" + formatted_phone[3:6] + "-" + formatted_phone[6:10]
            return cp_phone
        else:
            if prefix:
                formatted_phone = "+1" + formatted_phone
            return formatted_phone

    # ----------------------- MESSAGE SEARCH -------------------------#
    def search_messages(self):
        # Dialogue box for search query
        query = Querybox.get_string(title="Search All Messages")

        # If query is blank, disregard
        if query == None or query == "":
            return

        # Detect if query is a phone search pasted from ###-###-### masking sytle. Concert to searchable string
        if len(query) == 12 and query[3] == "-" and query[7] == "-":
            query = self.format_phone(query)

        messages = self.read_incoming_sms_from_share_drive()

        search_results = []
        for message in messages:
            if (query.lower() in str(message['body']).lower() or query in str(message['to_phone'])
                    or query in str(message['from_phone']) or query in str(message['date'])):
                search_results.append(message)
        if len(search_results) == 0:
            messagebox.showerror(title="No Messages Found", message="No Messages Found. Try Again.\n\n"
                                                                    "Phone Searches: Remove hyphens")
        self.st.config(state="normal")
        self.st.delete("1.0", END)
        self.st.config(state="disabled")
        self.print_sms_messages(search_results, len(search_results))

    # ----------------------- SEND TEXT MESSAGES -------------------------#
    def get_ntp_time(self):
        call = ntplib.NTPClient()
        ntp_pool = ['time1.google.com', 'time2.google.com', 'time3.google.com', 'time4.google.com']
        try:
            response = call.request(random.choice(ntp_pool), version=3)
        except NTPException:
            return self.get_ntp_time()
        else:
            t = datetime.fromtimestamp(response.tx_time)
            return t.strftime('%Y-%m-%d %H:%M:%S')

    def send_text(self):
        # Get Listbox Value, Present Message Box with Segment
        phone_number = self.format_phone(self.to_phone_box.get(), prefix=True)
        message = self.message_box.get("1.0", END)
        client = Client(account_sid, auth_token)
        client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number,
            body=message
        )

        (customer_name, customer_email, rewards_points,
         last_sale_date, customer_category) = self.query_db(self.format_phone(phone_number, mode="Counterpoint"))

        self.message_box.delete("1.0", END)

        log_data = [[str(self.get_ntp_time()), phone_number, TWILIO_PHONE_NUMBER, message.strip(),
                     userid, customer_name, customer_category]]
        df = pandas.DataFrame(log_data, columns=["date", "to_phone", "from_phone", "body",
                                                 "user", "name", "category"])

        if platform == "darwin":
            try:
                pandas.read_csv(creds.mac_outgoing_log_path)
            except FileNotFoundError:
                df.to_csv(creds.mac_outgoing_log_path, mode='a', header=True, index=False)
            else:
                df.to_csv(creds.mac_outgoing_log_path, mode='a', header=False, index=False)
        elif platform == "win32":
            try:
                pandas.read_csv(creds.windows_outgoing_log_path)
            except FileNotFoundError:
                df.to_csv(creds.windows_outgoing_log_path, mode='a', header=True, index=False)
            else:
                df.to_csv(creds.windows_outgoing_log_path, mode='a', header=False, index=False)

    def clear_scrolling_text(self):
        self.st.config(state="normal")
        self.st.delete("1.0", END)
        self.st.config(state="disabled")


    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return ("break")

    # def outgoing_message_checkbox_used(self):
    #     check = self.outgoing_messages_checkbox_state.get()
    #     if check == 0:
    #         return 0
    #     if check == 1:
    #         return 1


def application():
    login = LoginWindow()
    messenger = MessengerWindow()


application()
