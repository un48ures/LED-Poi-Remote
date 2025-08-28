import sys
import time
import tkinter as tk
from tkinter import ttk
import serial
from tkinter import *
import struct
import serial.tools.list_ports as port_list # Find connected Ports for Arduino

root = tk.Tk()
root.title("Remote Control LED Poi Sticks")

# Channels: 20 30 40 50 60 70
# Actually defined by Arduino itself
receiver_ids = [1, 2, 3, 4, 5, 6]

VIDEO_LIGHT_MODE_HW_BUTTONS = 0
VIDEO_LIGHT_MODE = 1
PICTURE_MODE = 2
SIGNAL_STRENGTH_TEST_MODE = 3

# Protocol:
# 1.byte - START_BYTE - for sync
# 2.byte - mode
# 3.byte - receiver id
# 4.byte - picture
# 5.byte - hue
# 6.byte - saturation
# 7.byte - brightness
# 8.byte - velocity

# Send bytes
def send(mode, receiver_id, picture, hue, saturation, brightness_value, velocity):
    starttime_SP_write = time.time_ns()

    START_BYTE = 0xAA
    packet = bytes([START_BYTE, int(mode), int(receiver_id), int(picture),
                    int(hue), int(saturation), int(brightness_value), int(velocity)])

    if serialPort is not None:
        serialPort.write(packet)
    else:
        print("No serial connection established - can`t write to serial Port")

    receive()

    print("Duration for serial port write and receive: " + str(
        (time.time_ns() - starttime_SP_write) / 1000000) + " ms")

def receive():
    if serialPort is None:
        return

    expected_bytes = 12 * 4  # 12 floats, 4 bytes each = 48 bytes

    if serialPort.in_waiting >= expected_bytes:
        try:
            raw_data = serialPort.read(expected_bytes)
            floats = struct.unpack('<12f', raw_data)  # Little-endian float
            voltages = [round(f, 3) for f in floats[:6]]
            signal_strength = floats[6:]
            inputb1.set(str(voltages[0]) + "V")
            inputb2.set(str(voltages[1]) + "V")
            inputb3.set(str(voltages[2]) + "V")
            inputb4.set(str(voltages[3]) + "V")
            inputb5.set(str(voltages[4]) + "V")
            inputb6.set(str(voltages[5]) + "V")
            inputss1.set(str(signal_strength[0]) + "%")
            inputss2.set(str(signal_strength[1]) + "%")
            inputss3.set(str(signal_strength[2]) + "%")
            inputss4.set(str(signal_strength[3]) + "%")
            inputss5.set(str(signal_strength[4]) + "%")
            inputss6.set(str(signal_strength[5]) + "%")
        except Exception as e:
            print(f"[Binary Receive] Error: {e}")

def send_current_values():
    if receiver_select.get() == -1:  # Select all (-1)
        for identifier in receiver_ids:
            send(mode_select.get(), identifier, input_picture.get(), hslider.get(), sslider.get(), bslider.get(), vslider.get())

    else:
        send(mode_select.get(), receiver_select.get(), input_picture.get(), hslider.get(), sslider.get(), bslider.get(), vslider.get())


def send_off():
    if receiver_select.get() == -1:  # Select all (-1)
        for identifier in receiver_ids:
            send(mode_select.get(), identifier, 0, 0, 0, 0, 0)

    else:
        send(mode_select.get(), receiver_select.get(), 0, 0, 0, 0, 0)


def input_inc():
    tmp = input_picture.get()
    tmp = tmp + 1
    input_picture.set(tmp)
    send_current_values()

def input_dec():
    tmp = input_picture.get()
    if tmp > 0:
        tmp = tmp - 1
    input_picture.set(tmp)
    send_current_values()

# Apply selected COM Port
def apply():
    serialPort.setPort(combo.get().split()[0])


# Title/Labels
title = tk.Label(root, bg="yellow", text="Remote Control LED Poi")
title.grid(row=0, column=0, sticky="W")

# Mode Label
modeLabel = tk.Label(root, bg="white", text="Mode", anchor="n")
modeLabel.grid(row=1, column=0)
# Mode Radio Buttons
mode_select = tk.IntVar()
mode_select.set(2)
# Mode Video Light - Hardware Buttons
radiom0 = tk.Radiobutton(root, text="Video Light Mode - HW Buttons", value=0, variable=mode_select)
radiom0.grid(row=2, column=0, sticky="W")
# Mode Video Light - Remote
radiom1 = tk.Radiobutton(root, text="Video Light Mode - Remote", value=1, variable=mode_select)
radiom1.grid(row=3, column=0, sticky="W")
# Mode Picture Mode
radiom2 = tk.Radiobutton(root, text="Picture Mode", value=2, variable=mode_select)
radiom2.grid(row=4, column=0, sticky="W")
# Mode Battery Level / Signal Strength
radiom3 = tk.Radiobutton(root, text="Battery Level / Signal Strength", value=3, variable=mode_select)
radiom3.grid(row=5, column=0, sticky="W")

# List available COM Ports
ports = list(port_list.comports())
for p in ports:
    print(p)

# COMBO BOX for COM Port
combo = ttk.Combobox(root, state="readonly", values=ports)
combo.grid(row=8, column=0)

if len(ports) > 0:
    # Take first COM Port of List as default
    serialPort = serial.Serial(port=str(ports[0]).split()[0], baudrate=115200, bytesize=8, timeout=2,
                               stopbits=serial.STOPBITS_ONE)
    combo.set(ports[0])

# Button Apply
buttonA = tk.Button(root, bg="white", text="Apply", anchor="e", command=apply)
buttonA.grid(row=8, column=1, sticky="w", padx=10)

# Select Picture Nr. Label
inputlabel = tk.Label(root, bg="white", text="Select Picture Nr.", anchor="n")
inputlabel.grid(row=1, column=1)
# Input Box Select Picture Nr.
input_picture = tk.IntVar()
input_picture.set(0)
inputbox = tk.Entry(root, textvariable=input_picture, width=5)
inputbox.grid(row=2, column=1, padx=20)
# Button Plus
buttonplus = tk.Button(root, bg="white", text="+", anchor="w", command=input_inc)
buttonplus.grid(row=2, column=1, sticky="e")
# Button Minus
buttonminus = tk.Button(root, bg="white", text="-", anchor="e", command=input_dec)
buttonminus.grid(row=2, column=1, sticky="w", padx=10)
# Button Send
button1 = tk.Button(root, text="Send", highlightthickness="6", command=send_current_values)
button1.grid(row=3, column=1)
# Button Off
button2 = tk.Button(root, text="Off", highlightthickness="6", command=send_off)
button2.grid(row=4, column=1)

# Select Receiver ID Label
channel = tk.Label(root, bg="white", text="Select Receiver ID")
channel.grid(row=1, column=4, padx=10)
# Radiobuttons receiver IDs
receiver_select = tk.IntVar()
for ids in receiver_ids:
    radiob = tk.Radiobutton(root, text=ids, value=ids, variable=receiver_select)
    radiob.grid(row=int(ids + 1), column=4)  # row 4 - 9
radio_all = tk.Radiobutton(root, text="all", value=-1, variable=receiver_select)
radio_all.grid(row=8, column=4)
receiver_select.set(-1)  # setdefault to CH 20

# Slider brightness/value Label
bright_label = tk.Label(root, bg="white", text="Brightness/Value", anchor="n")
bright_label.grid(row=1, column=5)
# Slider brightness input
bslider = tk.Scale(root, from_=0, to=40, orient=HORIZONTAL)
bslider.grid(row=2, column=5)
bslider.set(5)  # default

# Slider Hue Label
hue_label = tk.Label(root, bg="white", text="Hue", anchor="n")
hue_label.grid(row=1, column=6)
# Slider Hue input
hslider = tk.Scale(root, from_=0, to=255, orient=HORIZONTAL)
hslider.grid(row=2, column=6)
hslider.set(1)  # default

# Slider Saturation Label
sat_label = tk.Label(root, bg="white", text="Saturation")
sat_label.grid(row=1, column=7)
# Slider Saturation input
sslider = tk.Scale(root, from_=0, to=255, orient=HORIZONTAL)
sslider.grid(row=2, column=7)
sslider.set(1)  # default

# Slider velocity Label
vel_label = tk.Label(root, bg="white", text="Velocity", anchor="n")
vel_label.grid(row=1, column=8)
# Slider brightness input
vslider = tk.Scale(root, from_=0, to=60, orient=HORIZONTAL)
vslider.grid(row=2, column=8)
vslider.set(25)  # default

# Battery Level Label
inputlabel = tk.Label(root, bg="white", text="Battery Level")
inputlabel.grid(row=1, column=9)
batteryBoxWidth = 10
# Input Box Battery 1
inputb1 = tk.StringVar()
inputb1.set('0.0V')
inputbox = tk.Entry(root, textvariable=inputb1, width=batteryBoxWidth)
inputbox.grid(row=2, column=9, padx=20)
# Input Box Battery 2
inputb2 = tk.StringVar()
inputb2.set('0.0V')
inputbox = tk.Entry(root, textvariable=inputb2, width=batteryBoxWidth)
inputbox.grid(row=3, column=9, padx=20)
# Input Box Battery 3
inputb3 = tk.StringVar()
inputb3.set('0.0V')
inputbox = tk.Entry(root, textvariable=inputb3, width=batteryBoxWidth)
inputbox.grid(row=4, column=9, padx=20)
# Input Box Battery 4
inputb4 = tk.StringVar()
inputb4.set('0.0V')
inputbox = tk.Entry(root, textvariable=inputb4, width=batteryBoxWidth)
inputbox.grid(row=5, column=9, padx=20)
# Input Box Battery 5
inputb5 = tk.StringVar()
inputb5.set('0.0V')
inputbox = tk.Entry(root, textvariable=inputb5, width=batteryBoxWidth)
inputbox.grid(row=6, column=9, padx=20)
# Input Box Battery 6
inputb6 = tk.StringVar()
inputb6.set('0.0V')
inputbox = tk.Entry(root, textvariable=inputb6, width=batteryBoxWidth)
inputbox.grid(row=7, column=9, padx=20)

SignalBoxWidth = 10
# Signal Strength Level Label
inputlabel = tk.Label(root, bg="white", text="Signal Strength")
inputlabel.grid(row=1, column=10)
batteryBoxWidth = 10
# Input Box Signal Strength 1
inputss1 = tk.StringVar()
inputss1.set('0%')
inputbox = tk.Entry(root, textvariable=inputss1, width=SignalBoxWidth)
inputbox.grid(row=2, column=10, padx=20)
# Input Box Signal Strength 2
inputss2 = tk.StringVar()
inputss2.set('0%')
inputbox = tk.Entry(root, textvariable=inputss2, width=SignalBoxWidth)
inputbox.grid(row=3, column=10, padx=20)
# Input Box Signal Strength 3
inputss3 = tk.StringVar()
inputss3.set('0%')
inputbox = tk.Entry(root, textvariable=inputss3, width=SignalBoxWidth)
inputbox.grid(row=4, column=10, padx=20)
# Input Box Signal Strength 4
inputss4 = tk.StringVar()
inputss4.set('0%')
inputbox = tk.Entry(root, textvariable=inputss4, width=SignalBoxWidth)
inputbox.grid(row=5, column=10, padx=20)
# Input Box Signal Strength 5
inputss5 = tk.StringVar()
inputss5.set('0%')
inputbox = tk.Entry(root, textvariable=inputss5, width=SignalBoxWidth)
inputbox.grid(row=6, column=10, padx=20)
# Input Box Signal Strength 6
inputss6 = tk.StringVar()
inputss6.set('0%')
inputbox = tk.Entry(root, textvariable=inputss6, width=SignalBoxWidth)
inputbox.grid(row=7, column=10, padx=20)

mode_select_old = mode_select.get()
hue_slider_old = hslider.get()
brightness_slider_old = bslider.get()
velocity_slider_old = vslider.get()


def mode_refresher():
    global mode_select_old, hue_slider_old, brightness_slider_old, velocity_slider_old
    #while not stop_event.is_set():
    current_mode = mode_select.get()
    if current_mode != mode_select_old:
        send_current_values()

    if current_mode == SIGNAL_STRENGTH_TEST_MODE:
        receive()

    if current_mode == VIDEO_LIGHT_MODE:  # Send if hue value slider moved
        if hslider.get() != hue_slider_old or bslider.get() != brightness_slider_old:
            hue_slider_old = hslider.get()
            brightness_slider_old = bslider.get()
            send_current_values()

    if current_mode == PICTURE_MODE:  # Send if hue value slider moved
        if vslider.get() != velocity_slider_old or bslider.get() != brightness_slider_old:
            velocity_slider_old = vslider.get()
            brightness_slider_old = bslider.get()
            send_current_values()

    if mode_select_old != current_mode:
        mode_select_old = current_mode
    root.after(250, mode_refresher)


def exit_program():
    print("EXit")
    send_off()
    serialPort.close()
    root.destroy()

# Exit Button
buttonExit = tk.Button(root, text="Exit", command=exit_program)
buttonExit.grid(row=9, column=11)

# Main
root.after(250, mode_refresher) # Call mode refresher every 250ms
root.mainloop()

