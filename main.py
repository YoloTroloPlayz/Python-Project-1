import requests # test
import tkinter as tk
from tkinter import messagebox
import os
from dotenv import load_dotenv # modules
import json

load_dotenv()
API_KEY = os.getenv("API_KEY") # ga naar env file voor api key

# lijst tijdelijk opslaan favoriete haltes
temp_favorieten = []

def zoek_halte():
    zoekterm = entry_zoek.get().strip()
    if not zoekterm:
        messagebox.showwarning("Waarschuwing", "Vul eerst een plaats in!")
        return
    
    url = f"https://api.delijn.be/DLZoekOpenData/v1/zoek/haltes/{zoekterm}" # van de lijn api website
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}
    antwoord = requests.get(url, headers=headers) # reponse krijgen van api

    if antwoord.status_code != 200: # error als status niet ok
        messagebox.showerror("Fout", f"Status code {antwoord.status_code}")
        return

    data = antwoord.json()
    listbox_haltes.delete(0, tk.END)
    for halte in data.get("haltes", []):
        naam = halte.get("omschrijving")
        entiteitnummer = halte.get("entiteitnummer") # halte id
        listbox_haltes.insert(tk.END, f"{naam} (ID: {entiteitnummer})")

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
        # voeg ook toe aan tijdelijk of hij ze worden niet terug opgeslaan bij afsluiten
        temp_favorieten.append(item) 
        listbox_favorieten.insert(tk.END, item) 

root = tk.Tk()
root.title("De Lijn Haltezoeker")

# zoeken
frame_zoek = tk.Frame(root, padx=10, pady=10)
frame_zoek.pack(fill="x")

tk.Label(frame_zoek, text="Zoek halte:").pack(side="left")
entry_zoek = tk.Entry(frame_zoek, width=40)
entry_zoek.pack(side="left", padx=5)
tk.Button(frame_zoek, text="Zoek", command=zoek_halte).pack(side="left")

# haltes tonen
frame_result = tk.Frame(root, padx=10, pady=10)
frame_result.pack(fill="both", expand=True)

tk.Label(frame_result, text="Gevonden haltes:").pack(anchor="w")
listbox_haltes = tk.Listbox(frame_result, width=60, height=20)
listbox_haltes.pack(fill="both", expand=True)

# favorieten tonen (onder frame_result)
frame_favorites = tk.Frame(root, padx=10, pady=10)
frame_favorites.pack(fill="x")  

tk.Label(frame_favorites, text="Voeg toe aan favorieten:").pack(side="top", anchor="w")
tk.Button(frame_favorites, text="Voeg Toe", command=halte_favorieten).pack(side="top", anchor="w", pady=(0,10))

tk.Label(frame_favorites, text="Favoriete haltes:").pack(anchor="w", pady=(10,0))
listbox_favorieten = tk.Listbox(frame_favorites, width=60, height=8)
listbox_favorieten.pack(fill="both", expand=True)

tk.Label(frame_favorites, text="Verwijder uit favorieten:").pack(side="top", anchor="sw", pady=(10,0))
tk.Button(frame_favorites, text="Verwijder", command=halte_verwijderen_favorieten).pack(side="top", anchor="sw", pady=(0,10))

root.after(0, load_favorieten) # bij opstart
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
