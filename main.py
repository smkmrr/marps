from datetime import datetime
from datetime import timedelta
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from pynput import keyboard
import gpiozero


class WelcomePage(GridLayout):
    # runs on initialization
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2  # used for our grid

        label1 = Label(text="Welcome to A Village")
        warn_message = Label(text="Scan Your RfId tag")

        self.add_widget(label1)  # widget #1, top left
        self.add_widget(self.get_updating_time())
        self.add_widget(warn_message)  # widget #1, top left

    def get_updating_time(self):
        self.now = datetime.now()
        Clock.schedule_interval(self.update_clock, 1)
        self.my_label = Label(text=self.now.strftime('%H:%M:%S'))
        return self.my_label  # The label is the only widget in the interface

    def update_clock(self, *args):
        # Called once a second using the kivy.clock module
        # Add one second to the current time and display it on the label
        self.now = self.now + timedelta(seconds=1)
        self.my_label.text = self.now.strftime('%H:%M:%S')


class ErrorPage(GridLayout):
    # runs on initialization
    def __init__(self, message, **kwargs):
        super().__init__(**kwargs)

        self.cols = 1  # used for our grid

        error = Label(text=message)
        self.error = error
        self.add_widget(error)  # widget #1, top left
    # Called with a message, to update message text in widget
    def update_message(self, message):
        self.error.text = message


class CartPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Just one column
        self.cols = 1

        # And one label with bigger font and centered text
        self.message = Label(halign="center", valign="middle", font_size=30)
        self.forward = Button(text="Forward")
        self.forward.bind(on_press=self.getCheckoutPage)
        # Add text widget to the layout
        self.add_widget(self.message)
        self.add_widget(self.forward)

    # Called with a message, to update message text in widget
    def update_rfId(self, message):
        self.message.text = message

    def update_company_name(self, message):
        self.message.text = message

    def update_company_code(self, message):
        self.message.company_code = message

    def getCheckoutPage(self, message):
        marps_app.changePage()

class CheckoutPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Just one column
        self.cols = 1

        self.label = Label(text="Are you sure to checkout? make sure that the fridge is closed properly!")
        self.forward = Button(text="Yes")
        self.forward.bind(on_press=self.checkout)
        self.back = Button(text="No")
        self.back.bind(on_press=self.getCartPage)
        # Add text widget to the layout
        self.add_widget(self.label)
        self.add_widget(self.forward)
        self.add_widget(self.back)

    def checkout(self, message):

        marps_app.changePage()

    def getCartPage(self, message):
        marps_app.getCartPage()


class MarpsApp(App):

    def build(self):
        # We are going to use screen manager, so we can add multiple screens
        # and switch between them
        self.screen_manager = ScreenManager()

        # Initial, connection screen (we use passed in name to activate screen)
        # First create a page, then a new screen, add page to screen and screen to screen manager
        self.welcome_page = WelcomePage()
        screen = Screen(name='Welcome')
        screen.add_widget(self.welcome_page)
        self.screen_manager.add_widget(screen)

        self.cart_page = CartPage()
        screen = Screen(name='Cart')
        screen.add_widget(self.cart_page)
        self.screen_manager.add_widget(screen)

        self.error_page = ErrorPage("Empty")
        screen = Screen(name='Error')
        screen.add_widget(self.error_page)
        self.screen_manager.add_widget(screen)

        self.co_page = CheckoutPage()
        screen = Screen(name='Checkout')
        screen.add_widget(self.co_page)
        self.screen_manager.add_widget(screen)

        self.ty_page = ThankYouPage()
        screen = Screen(name='ThankYou')
        screen.add_widget(self.ty_page)
        self.screen_manager.add_widget(screen)

        self.screen_manager.current = "Welcome"
        return self.screen_manager

    def on_request_close(self, *args):
        fridge.lock()
        print("EXIT APPs")
        return True

    def changePage(self):
        if self.screen_manager.current == "Checkout":
            print("checkout -to- welcome")
            self.screen_manager.current = "Welcome"
            self.resetSession()
        elif self.screen_manager.current == "Cart":
            print("cart -to- checkout")
            self.screen_manager.current = "Checkout"
        elif self.screen_manager.current == "Welcome":
            print("welcome -to- cart")
            self.screen_manager.current = "Cart"
            self.cart_page.update_rfId(session["rfId"])
            self.cart_page.update_company_name(session["company_name"])
            fridge.unlock()
        else:
            self.resetSession()
            self.errorPage("No page found returning to Welcome")

    def getCartPage(self):
            self.screen_manager.current = "Cart"

    def resetSession(self):
        session["rfId"] = None
        session["company_name"] = None
        fridge.lock()

    def errorPage(self, message):
        self.error_page.update_message(message)
        self.screen_manager.current = "Error"
        time.sleep(3)
        self.screen_manager.current = "Welcome"


class RfReader():
    def __init__(self, **kwargs):
        self.key_list = []
        self.result = ""
        self.totalCount = 0

    def on_press(self, key):
        self.key_list.append(key)

        if len(self.key_list) % 11 == 0:
            try:
                self.convert()
            except:
                marps_app.errorPage("No Company Record Found")
                self.result = ""
                self.key_list = []
                self.totalCount += 1
                return
            self.result = ""
            self.key_list = []
            self.totalCount += 1
            print("card read count: " + str(self.totalCount))
            marps_app.changePage()

    def convert(self):
        for idx, val in enumerate(self.key_list[0:10]):
            self.result += str(self.key_list[idx]).replace("'", "")

        session["rfId"] = self.result
        session["company_name"] = database.getCompanyNameByRfId(session["rfId"])
        # session["company_code"] = database.getCompanyCodeByRfId(session["rfId"])

import pgdb


class PostgresDb():
    def __init__(self, **kwargs):
        self.connection = pgdb.connect(host="localhost", user="marps_db_user", password="marps_db_pass",
                                       database="marps_db")
        self.initDb()
        # myConnection.close()

    def getCompanyNameByRfId(self, rfId):
        cur = self.connection.cursor()
        print("RFID:", rfId)
        cur.execute("select companyId from villager where rfId='" + rfId + "'")
        companyid = cur.fetchone()
        print("company Id found:", companyid)
        if companyid is None:
            raise Exception("No company record found")
        cur.execute("select name from company where id=" + str(companyid[0]))
        return cur.fetchone()[0]

    # def getCompanyCodeByRfId(self, rfId):
    #     cur = self.connection.cursor()
    #     cur.execute("select id from villager where rfId='"+rfId+"'")
    #     companyid = cur.fetchone()
    #     cur.execute("select code from company where id=" + str(companyid[0]))
    #     return cur.fetchone()[0]

    def initDb(self):
        cur = self.connection.cursor()
        cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        tabels = len(cur.fetchall())
        print(tabels)
        if tabels == 0:
            print('::::::::::::tables will be created')
            insert = """CREATE TABLE company (
                id integer PRIMARY KEY,
                name VARCHAR ( 50 ) UNIQUE,
                code NUMERIC ( 10 ) NOT NULL,
                email VARCHAR ( 255 ) UNIQUE,
                created_on TIMESTAMP NOT NULL
            );
            
            INSERT INTO company(id, name, code, email, created_on) VALUES ( 102, 'Meganova', 1002, 'info@meganova.se', NOW());
            INSERT INTO company(id, name, code, email, created_on) VALUES ( 101, 'A Village', 1001, 'info@avillage.se', NOW());
            
            CREATE TABLE villager (
                id integer PRIMARY KEY,
                name VARCHAR ( 50 ) UNIQUE,
                rfId VARCHAR ( 10 ) NOT NULL,
                companyId integer not null references company(id),
                created_on TIMESTAMP NOT NULL
            );
        
            INSERT INTO villager(id, name, rfId, companyId, created_on) VALUES (123, 'Ali Akyel', '0000792099', 102, NOW());            
            INSERT INTO villager(id, name, rfId, companyId, created_on) VALUES (124, 'Deniz Ozen', '0005713678', 102, NOW());
            INSERT INTO villager(id, name, rfId, companyId, created_on) VALUES (127, 'Mesut Yilmaz', '0005728272', 101, NOW());"""

            cur.execute(insert)
            self.connection.commit()
        else:
            print('::::::::::::tables are already there')
    # postgreSQL_select_Query = "insert into mobile (id, model) values (123, 123);"
    # cur.execute(postgreSQL_select_Query)
    # conn.commit()

    # cur.execute( "SELECT \"id\",\"name\" FROM company;")
    # for name in cur.fetchall() :
    #     print( name )
    #
    # cur.execute("""SELECT table_name FROM information_schema.tables
    #    WHERE table_schema = 'public'""")
    # print("publicler lar:")
    # for table in cur.fetchall():
    #     print(table)


class Fridge():
    # create a relay object.
    # Triggered by the output pin going low: active_high=False.
    # Initially off: initial_value=False
    def __init__(self, **kwargs):
        self.relay1 = gpiozero.OutputDevice(3, active_high=False, initial_value=False)
        self.relay2 = gpiozero.OutputDevice(5, active_high=False, initial_value=False)
        self.lock()

    def lock(self):
        print("RELAY OFF")
        self.relay1.off()
        self.relay2.off()


    def unlock(self):
        print("RELAY ON")
        self.relay1.on()
        self.relay2.on()


marps_app = None
session = {}
database = None
fridge = None

if __name__ == "__main__":
    database = PostgresDb()
    reader = RfReader()
    fridge = Fridge()
    listener = keyboard.Listener(on_press=reader.on_press)
    listener.start()  # start to listen on a separate thread

    marps_app = MarpsApp()
    try:
        marps_app.run()
    except KeyboardInterrupt:
        marps_app.on_request_close()
        print("\nExiting application\n")

