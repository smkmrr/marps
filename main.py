
from kivy.clock import Clock
from datetime import timedelta
from datetime import datetime
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from pynput import keyboard


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


class CartPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Just one column
        self.cols = 1

        # And one label with bigger font and centered text
        self.message = Label(halign="center", valign="middle", font_size=30)

        # By default every widget returns it's side as [100, 100], it gets finally resized,
        # but we have to listen for size change to get a new one
        # more: https://github.com/kivy/kivy/issues/1044
        self.message.bind(width=self.update_text_width)

        # Add text widget to the layout
        self.add_widget(self.message)

    # Called with a message, to update message text in widget
    def update_rfId(self, message):
        self.message.text = message

    def update_company_name(self, message):
        self.message.text = message

    def update_company_code(self, message):
        self.message.company_code = message
    # Called on label width update, so we can set text width properly - to 90% of label width
    def update_text_width(self, *_):
        self.message.text_size = (self.message.width * 0.9, None)


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
        self.screen_manager.current = "Welcome"
        return self.screen_manager

    def changePage(self):
        if self.screen_manager.current == "Cart" :
            self.screen_manager.current = "Welcome"
        else:
            self.screen_manager.current = "Cart"
            self.cart_page.update_rfId(session["rfId"])
            self.cart_page.update_company_name(session["company_name"])
            # self.cart_page.update_company_code(session["company_code"])


class RfReader():
    def __init__(self, **kwargs):
        self.key_list = []
        self.result = ""
        self.totalCount = 0

    def on_press(self, key):
        self.key_list.append(key)

        step = 0
        if len(self.key_list) % 11 == 0 & step == 0:
            self.convert()
            self.key_list = []
            self.totalCount += 1
            print( "card read count: " + str(self.totalCount))
            step = 1
            marps_app.changePage()

    def convert(self):
        for idx, val in enumerate(self.key_list[0:10]):
            self.result +=  str(self.key_list[idx]).replace("'", "")

        session["rfId"] = self.result
        session["company_name"] = database.getCompanyNameByRfId(session["rfId"])
        # session["company_code"] = database.getCompanyCodeByRfId(session["rfId"])
        print (self.result)
        self.result = ""

import pgdb

class PostgresDb():
    def __init__(self, **kwargs):
        self.connection = pgdb.connect(host="localhost", user="postgres", password="12", database="marps_db")
        self.initDb()

        # myConnection.close()

    def getCompanyNameByRfId(self, rfId):
        cur = self.connection.cursor()
        cur.execute("select companyId from villager where rfId='"+rfId+"'")
        companyid = cur.fetchone()
        cur.execute("select name from company where id="+str(companyid[0]))
        return cur.fetchone()[0]


    # def getCompanyCodeByRfId(self, rfId):
    #     cur = self.connection.cursor()
    #     cur.execute("select id from villager where rfId='"+rfId+"'")
    #     companyid = cur.fetchone()
    #     cur.execute("select code from company where id=" + str(companyid[0]))
    #     return cur.fetchone()[0]

    def initDb(self) :
        cur = self.connection.cursor()
        cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        tabels = len(cur.fetchall())
        print(tabels)
        if tabels == 0 :
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

    #postgreSQL_select_Query = "insert into mobile (id, model) values (123, 123);"
    #cur.execute(postgreSQL_select_Query)
    #conn.commit()

    # cur.execute( "SELECT \"id\",\"name\" FROM company;")
    # for name in cur.fetchall() :
    #     print( name )
    #
    # cur.execute("""SELECT table_name FROM information_schema.tables
    #    WHERE table_schema = 'public'""")
    # print("publicler lar:")
    # for table in cur.fetchall():
    #     print(table)


marps_app = None
session = { }
database = None

if __name__ == "__main__":
    database = PostgresDb()
    reader = RfReader()
    listener = keyboard.Listener(on_press=reader.on_press)
    listener.start()  # start to listen on a separate thread

    marps_app = MarpsApp()
    marps_app.run()


