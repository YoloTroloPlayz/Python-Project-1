import requests 
import tkinter as tk
from tkinter import messagebox
import os
from dotenv import load_dotenv # modules
import json
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("API_KEY") # ga naar env file voor api key
datum = datetime.now().strftime("%Y-%m-%d")  # huidige datum in yyyy-MM-dd format

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

def get_haltesleutels(entiteitnummer, haltenummer):
    url3 = f"https://api.delijn.be/DLKernOpenData/v1/haltes/{entiteitnummer}/{haltenummer}"
    headers3 = {"Ocp-Apim-Subscription-Key": API_KEY}
    antwoord3 = requests.get(url3, headers=headers3)
    if antwoord3.status_code != 200:
        raise RuntimeError(f"Fout bij haltesleutels: status {antwoord3.status_code}")
    data3 = antwoord3.json()
    return data3.get("haltesleutels")

def zoek_omleidingen():
    # veiligheden bij gebruik van selectie
    try:
        geselecteerde_halte = listbox_haltes.get(listbox_haltes.curselection())
    except (tk.TclError, IndexError):
        messagebox.showwarning("Waarschuwing", "Selecteer een halte.")
        return

    try:
        id_part = geselecteerde_halte.split("ID:")[-1].strip()
        if id_part.endswith(")"):
            id_part = id_part[:-1].strip()
        entiteitnummer, haltenummer = id_part.split("-", 1)
    except Exception:
        messagebox.showerror("Fout", "Kon halte-ID niet uitlezen. Verwacht format: 'Naam (ID: entiteit-haltenummer)'.")
        return

    try:
        haltesleutels = get_haltesleutels(entiteitnummer, haltenummer)
    except Exception as e:
        messagebox.showerror("Fout", f"Fout bij ophalen haltesleutels: {e}")
        return
    
    if not haltesleutels:
        messagebox.showinfo("Info", "Geen haltesleutels gevonden.")
        return

    # vanaf hier API requests en in listbox steken
    url2 = f"https://api.delijn.be/DLKernOpenData/api/v1/haltes/lijst/{haltesleutels}/omleidingen?datum={datum}"
    headers2 = {"Ocp-Apim-Subscription-Key": API_KEY}
    antwoord2 = requests.get(url2, headers=headers2)
    if antwoord2.status_code != 200:
        messagebox.showerror("Fout", f"Status code {antwoord2.status_code}")
        return

    data2 = antwoord2.json()
    listbox_omleidingen.delete(0, tk.END)
    for item in data2.get("halteOmleidingen", []):
        for oml in item.get("omleidingen", []):
            for lr in oml.get("lijnrichtingen", []):
                listbox_omleidingen.insert(tk.END, f"Lijn {lr.get('lijnNummerPubliek')} naar {lr.get('bestemming')}")


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
root.geometry("1200x600")  # afmetingen form

# main frame
frame_top = tk.Frame(root)
frame_top.pack(fill="both", expand=True, padx=10, pady=10)

# zoeken
frame_zoek = tk.Frame(frame_top, padx=5, pady=5, relief="ridge", borderwidth=1)
frame_zoek.pack(side="left", fill="both", expand=True)

tk.Label(frame_zoek, text="Zoek halte:").pack(anchor="w")
entry_zoek = tk.Entry(frame_zoek, width=20)
entry_zoek.pack(anchor="w")
tk.Button(frame_zoek, text="Zoek", command=zoek_halte).pack(anchor="w", pady=5)

tk.Label(frame_zoek, text="Gevonden haltes:").pack(anchor="w", pady=(10,0))
listbox_haltes = tk.Listbox(frame_zoek, width=25, height=15)
listbox_haltes.pack(fill="both", expand=True, padx=5, pady=5)

# favorieten 
frame_favorites = tk.Frame(frame_top, padx=5, pady=5, relief="ridge", borderwidth=1)
frame_favorites.pack(side="left", fill="both", expand=True, padx=5)

tk.Label(frame_favorites, text="Voeg toe:").pack(anchor="w")
tk.Button(frame_favorites, text="Voeg Toe", command=halte_favorieten).pack(anchor="w", pady=5)

tk.Label(frame_favorites, text="Favorieten:").pack(anchor="w", pady=(10,0))
listbox_favorieten = tk.Listbox(frame_favorites, width=25, height=10)
listbox_favorieten.pack(fill="both", expand=True, padx=5, pady=5)

tk.Button(frame_favorites, text="Verwijder", command=halte_verwijderen_favorieten).pack(anchor="w", pady=5)

# omleidingen 
frame_omleidingen = tk.Frame(frame_top, padx=5, pady=5, relief="ridge", borderwidth=1)
frame_omleidingen.pack(side="left", fill="both", expand=True, padx=5)

tk.Label(frame_omleidingen, text="Omleidingen lijn").pack(anchor="w")
tk.Button(frame_omleidingen, text="Zie", command=zoek_omleidingen).pack(anchor="w", pady=5)
listbox_omleidingen = tk.Listbox(frame_omleidingen, width=25, height=15)
listbox_omleidingen.pack(fill="both", expand=True, padx=5, pady=5)

root.after(0, load_favorieten)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
