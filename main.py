import requests # packages
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv 
import os # modules
import json
from datetime import datetime, timedelta

load_dotenv()
API_KEY = os.getenv("API_KEY") # ga naar env file voor api key
datum = datetime.now().strftime("%Y-%m-%d")  # huidige datum in yyyy-MM-dd format

# lijst tijdelijk opslaan favoriete haltes
temp_favorieten = []

# klasse voor het uitvoeren van API aanvragen
class APIRequest:
    def __init__(self, api_key):
        self.headers = {"Ocp-Apim-Subscription-Key": api_key}

    def get(self, url):
        antwoord = requests.get(url, headers=self.headers)
        if antwoord.status_code != 200:
            raise Exception(f"Status code {antwoord.status_code}")
        return antwoord.json()

# subklasse specifieke API endpoints bevat en erft van APIRequest
class DeLijnAPI(APIRequest):
    def __init__(self, api_key):
        super().__init__(api_key)

    def zoek_haltes(self, zoekterm):
        url = f"https://api.delijn.be/DLZoekOpenData/v1/zoek/haltes/{zoekterm}"
        return self.get(url)

    def zoek_omleidingen(self):
        url = "https://api.delijn.be/DLKernOpenData/api/v1/omleidingen"
        return self.get(url)

api = DeLijnAPI(API_KEY)

def zoek_halte():
    zoekterm = entry_zoek.get().strip()
    if not zoekterm:
        messagebox.showwarning("Waarschuwing", "Vul eerst een plaats in!")
        return
    
    try:
        data = api.zoek_haltes(zoekterm)
    except Exception as e:
        messagebox.showerror("Fout", str(e))
        return

    listbox_haltes.delete(0, tk.END)
    for halte in data.get("haltes", []):
        naam = halte.get("omschrijving")
        entiteitnummer = halte.get("entiteitnummer") # halte id
        haltenummer = halte.get("haltenummer")
        listbox_haltes.insert(tk.END, f"{naam} (ID: {entiteitnummer}-{haltenummer})")

def zoek_omleidingen():
    try:
        data2 = api.zoek_omleidingen()
    except Exception as e:
        messagebox.showerror("Fout", str(e))
        return

    listbox_omleidingen.delete(0, tk.END)

    for omleiding in data2.get("omleidingen", []):
        titel = omleiding.get("titel", "Geen titel")
        start = omleiding.get("periode", {}).get("startDatum", "?")
        eind = omleiding.get("periode", {}).get("eindDatum", "?")

        listbox_omleidingen.insert(tk.END, f"━ {titel}")
        listbox_omleidingen.insert(tk.END, f"  Periode: {start} tot {eind}")
        listbox_omleidingen.insert(tk.END, "") # lege regel voor scheiding
        
def halte_favorieten():
    favoriet = listbox_haltes.selection_get()
    listbox_favorieten.insert(tk.END, favoriet)
    temp_favorieten.append(favoriet)

def halte_verwijderen_favorieten():
    geselecteerde_item = listbox_favorieten.curselection()[0]
    geselecteerde_inhoud = listbox_favorieten.get(geselecteerde_item)
    temp_favorieten.remove(geselecteerde_inhoud)
    listbox_favorieten.delete(geselecteerde_item)

def on_closing(): # bij afsluiten alle favorieten opslaan in een json
    try:
        with open("favorieten.json", "w", encoding="utf-8") as f:
            json.dump(temp_favorieten, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Fout opgelopen bij opslaan van jouw favorieten", e)
    root.destroy()

def load_favorieten(): # bij opstarten favorieten inladen uit json
    try:
        with open("favorieten.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception as e:
        print("Error bij inladen:", e)
        return

    temp_favorieten.clear()
    for item in items:
        temp_favorieten.append(item) 
        listbox_favorieten.insert(tk.END, item) 

root = tk.Tk()
root.title("De Lijn Haltezoeker")
root.geometry("1200x600")  # afmetingen form

frame_top = tk.Frame(root)
frame_top.pack(fill="both", expand=True, padx=10, pady=10)

frame_zoek = tk.Frame(frame_top, padx=5, pady=5, relief="ridge", borderwidth=1)
frame_zoek.pack(side="left", fill="both", expand=True)

tk.Label(frame_zoek, text="Zoek halte:").pack(anchor="w")
entry_zoek = tk.Entry(frame_zoek, width=20)
entry_zoek.pack(anchor="w")
tk.Button(frame_zoek, text="Zoek", command=zoek_halte).pack(anchor="w", pady=5)

tk.Label(frame_zoek, text="Gevonden haltes:").pack(anchor="w", pady=(10,0))
listbox_haltes = tk.Listbox(frame_zoek, width=25, height=15)
listbox_haltes.pack(fill="both", expand=True, padx=5, pady=5)

frame_favorites = tk.Frame(frame_top, padx=5, pady=5, relief="ridge", borderwidth=1)
frame_favorites.pack(side="left", fill="both", expand=True, padx=5)

tk.Label(frame_favorites, text="Voeg toe:").pack(anchor="w")
tk.Button(frame_favorites, text="Voeg Toe", command=halte_favorieten).pack(anchor="w", pady=5)

tk.Label(frame_favorites, text="Favorieten:").pack(anchor="w", pady=(10,0))
listbox_favorieten = tk.Listbox(frame_favorites, width=25, height=10)
listbox_favorieten.pack(fill="both", expand=True, padx=5, pady=5)

tk.Button(frame_favorites, text="Verwijder", command=halte_verwijderen_favorieten).pack(anchor="w", pady=5)

frame_omleidingen = tk.Frame(frame_top, padx=5, pady=5, relief="ridge", borderwidth=1)
frame_omleidingen.pack(side="left", fill="both", expand=True, padx=5)

tk.Label(frame_omleidingen, text="Omleidingen Delijn").pack(anchor="w")
tk.Button(frame_omleidingen, text="Geef alles weer", command=zoek_omleidingen).pack(anchor="w", pady=5)
listbox_omleidingen = tk.Listbox(frame_omleidingen, width=25, height=15)
listbox_omleidingen.pack(fill="both", expand=True, padx=5, pady=5)

root.after(0, load_favorieten)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
