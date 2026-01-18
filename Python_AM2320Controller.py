import serial
import serial.tools.list_ports
import csv
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# -----------------------------
# USER SETTINGS
# -----------------------------
BAUD = 115200
LOG_INTERVAL = 30   # seconds
CSV_FILE = "am2320_log.csv"

# -----------------------------
# DATA STORAGE
# -----------------------------
timestamps = []
temps = []
hums = []
resistances = []

running = False
ser = None

# -----------------------------
# SERIAL READER THREAD
# -----------------------------
def serial_reader(port):
    global running, ser

    try:
        ser = serial.Serial(port, BAUD, timeout=2)
    except Exception as e:
        messagebox.showerror("Connection Error", f"Could not open port {port}\n{e}")
        running = False
        return

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if f.tell() == 0:
            writer.writerow(["timestamp", "temp_C", "hum_pct", "adc_A1", "Vout_A1", "Rsensor_ohm"])

        while running:
            line = ser.readline().decode().strip()
            if not line:
                continue

            parts = line.split(",")
            if len(parts) != 6:
                continue

            _, temp, hum, adc, vout, rs = parts

            ts = datetime.now()

            writer.writerow([ts.strftime("%Y-%m-%d %H:%M:%S"), temp, hum, adc, vout, rs])
            f.flush()

            timestamps.append(ts)
            temps.append(float(temp))
            hums.append(float(hum))
            resistances.append(float(rs))

            temp_label.config(text=f"{float(temp):.2f} °C")
            hum_label.config(text=f"{float(hum):.2f} %")
            res_label.config(text=f"{float(rs):.1f} Ω")

            update_plot()
            time.sleep(LOG_INTERVAL)

    ser.close()

# -----------------------------
# START / STOP LOGGING
# -----------------------------
def start_logging():
    global running

    if running:
        return

    port = port_var.get()
    if not port:
        messagebox.showwarning("No Port Selected", "Please select a COM port first.")
        return

    running = True
    threading.Thread(target=serial_reader, args=(port,), daemon=True).start()

def stop_logging():
    global running
    running = False

# -----------------------------
# PLOT SETUP
# -----------------------------
fig, ax = plt.subplots(3, 1, figsize=(6, 7))
plt.tight_layout()

def update_plot():
    for a in ax:
        a.clear()

    if len(timestamps) > 0:
        ax[0].plot(timestamps, temps, color="red")
        ax[1].plot(timestamps, hums, color="blue")
        ax[2].plot(timestamps, resistances, color="green")

    ax[0].set_title("Temperature (°C)")
    ax[1].set_title("Humidity (%)")
    ax[2].set_title("Sensor Resistance (Ω)")

    for a in ax:
        a.tick_params(axis='x', rotation=45)

    fig.tight_layout()
    canvas.draw()

# -----------------------------
# TKINTER GUI
# -----------------------------
root = tk.Tk()
root.title("AM2320 + Resistive Sensor Logger")

# COM Port Selection
port_frame = ttk.Frame(root)
port_frame.pack(pady=10)

ttk.Label(port_frame, text="Select COM Port:", font=("Arial", 12)).grid(row=0, column=0)

port_var = tk.StringVar()
port_dropdown = ttk.Combobox(port_frame, textvariable=port_var, width=20)
ports = [p.device for p in serial.tools.list_ports.comports()]
port_dropdown['values'] = ports
port_dropdown.grid(row=0, column=1, padx=10)

def refresh_ports():
    ports = [p.device for p in serial.tools.list_ports.comports()]
    port_dropdown['values'] = ports

refresh_btn = ttk.Button(port_frame, text="Refresh", command=refresh_ports)
refresh_btn.grid(row=0, column=2, padx=10)

# Current readings
frame = ttk.Frame(root)
frame.pack(pady=10)

ttk.Label(frame, text="Temperature:", font=("Arial", 12)).grid(row=0, column=0)
temp_label = ttk.Label(frame, text="-- °C", font=("Arial", 12, "bold"))
temp_label.grid(row=0, column=1, padx=10)

ttk.Label(frame, text="Humidity:", font=("Arial", 12)).grid(row=1, column=0)
hum_label = ttk.Label(frame, text="-- %", font=("Arial", 12, "bold"))
hum_label.grid(row=1, column=1, padx=10)

ttk.Label(frame, text="Resistance:", font=("Arial", 12)).grid(row=2, column=0)
res_label = ttk.Label(frame, text="-- Ω", font=("Arial", 12, "bold"))
res_label.grid(row=2, column=1, padx=10)

# Buttons
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=10)

start_btn = ttk.Button(btn_frame, text="Start Logging", command=start_logging)
start_btn.grid(row=0, column=0, padx=10)

stop_btn = ttk.Button(btn_frame, text="Stop Logging", command=stop_logging)
stop_btn.grid(row=0, column=1, padx=10)

# Plot area
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

root.mainloop()
