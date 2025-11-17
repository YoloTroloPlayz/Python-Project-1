import requests
import tkinter as tk
from tkinter import messagebox
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

# 🔑 Jouw actieve ZoekOpenData key
API_KEY = "f21941ed60c84a808716ca909fe35aca"

def zoek_halte():
    zoekterm = entry_zoek.get().strip()
    if not zoekterm:
        messagebox.showwarning("Waarschuwing", "Vul eerst een zoekterm in!")
        return
    
    url = f"https://api.delijn.be/DLZoekOpenData/v1/zoek/haltes/{zoekterm}"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}
    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        messagebox.showerror("Fout", f"Status code {resp.status_code}")
        return

    data = resp.json()
    listbox_haltes.delete(0, tk.END)
    for halte in data.get("haltes", []):
        naam = halte.get("omschrijving")
        entiteitnummer = halte.get("entiteitnummer")
        listbox_haltes.insert(tk.END, f"{naam} (ID: {entiteitnummer})")

# --- GUI setup ---
root = tk.Tk()
root.title("De Lijn Haltezoeker")

# Zoek frame
frame_zoek = tk.Frame(root, padx=10, pady=10)
frame_zoek.pack(fill="x")

tk.Label(frame_zoek, text="Zoek halte:").pack(side="left")
entry_zoek = tk.Entry(frame_zoek, width=40)
entry_zoek.pack(side="left", padx=5)
tk.Button(frame_zoek, text="Zoek", command=zoek_halte).pack(side="left")

# Resultaten frame
frame_result = tk.Frame(root, padx=10, pady=10)
frame_result.pack(fill="both", expand=True)

tk.Label(frame_result, text="Gevonden haltes:").pack(anchor="w")
listbox_haltes = tk.Listbox(frame_result, width=60, height=20)
listbox_haltes.pack(fill="both", expand=True)

root.mainloop()
