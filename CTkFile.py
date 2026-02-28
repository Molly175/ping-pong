from customtkinter import *
from time import sleep
import json

class MainWindow(CTk):
    def __init__(self):
        CTk.__init__(self)
        self.geometry("100x50")
        self.title("Ping-Pong: Edit name")
        self.resizable(False, False)

        with open("data.json", "r") as f:
            data = json.load(f)
            self.new_name = data["name"]
        self.name_entry = CTkEntry(self)
        self.name_entry.pack()
        self.save_name = CTkButton(self, text="Save name", command=self.save_name)
        self.save_name.pack()
    def save_name(self):
        self.new_name = self.name_entry.get()
        with open("data.json", "r") as f:
            data = json.load(f)
            data["name"] = self.new_name
        with open("data.json", "w") as f:
            json.dump(data, f)

        sleep(0.1)
        self.destroy()