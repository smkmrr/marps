import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class MarpsApp (App):

    def build(self):
        l1 = Label(text="Welcome to A Village!")
        now = datetime.datetime.now()
        part1 = "Current data and time : "
        part2 = now.strftime("%Y-%m-%d %H:%M:%S")
        l2 = Label(text= part1 + part2)
        l3 = Label(text="Scan your RfId please")
        layout = BoxLayout(padding=10)
        layout.add_widget(l1)
        layout.add_widget(l2)
        layout.add_widget(l3)
        return layout