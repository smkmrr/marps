
#from com.meganova.marpsApp import MarpsApp
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
    def update_info(self, message):
        self.message.text = message

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
            self.cart_page.update_info(session["rfId"])


class RfReader():
    def __init__(self, **kwargs):
        self.key_list = []
        self.result = ""
        self.totalCount = 0

    def on_press(self, key):
        self.key_list.append(key)

        if len(self.key_list) % 11 == 0:
            self.convert()
            self.key_list = []
            self.totalCount += 1
            print( "card read count: " + str(self.totalCount))
            marps_app.changePage()

    def convert(self):
        for idx, val in enumerate(self.key_list[0:10]):
            self.result +=  str(self.key_list[idx]).replace("'", "")

        session["rfId"] = self.result
        print (self.result)
        self.result = ""



class mydatabase():

    def __init__(self):
        self.db = mysql.connector.connect(**config)
        self.c = self.db.cursor()

    def get_rows(self):
        # a,b,c,d depence of your database structure and tables
        # use the query example below, query needs parenthesis obligated

        query = ('SELECT {} FROM {} WHERE({}='')'.format("a", "b", "c", "d"))
        self.c.execute(query)
        return self.c.fetchall()

config = {'user': 'postgres',
          'password': 'mysecretpassword',
          'host': 'localhost:5432',
          'database': 'insert_database_name',
          'raise_on_warnings': True}
marps_app = None
session = { }

if __name__ == "__main__":
    reader = RfReader()
    listener = keyboard.Listener(on_press=reader.on_press)
    listener.start()  # start to listen on a separate thread
 #   usbListener = UsbListener()
    marps_app = MarpsApp()
    marps_app.run()


