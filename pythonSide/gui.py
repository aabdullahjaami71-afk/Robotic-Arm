from tkinter import *
from tkinter import filedialog
import arm_control
import json
from ik import open_ik_library

BGcolor = "darkred"

simulation_mode = False   
poll_job = None     

window = Tk()
window.geometry("700x500")
window.title("RoboArm")
window.configure(bg=BGcolor)

joints = ["Gripper", "Wrist", "Shoulder", "Elbow", "Base"]

slider_frame = Frame(window, bg=BGcolor)
slider_frame.place(x=20, y=20, width=250, height=460)

sliders = {}
recorded = []


def send(angles):
    if simulation_mode:
        return "simulation_mode"
    return arm_control.send_angles(angles)


def set_angles():
    angles = [sliders[joint].get() for joint in joints]
    status_label.config(text="Sweeping...")
    window.update()

    response = send(angles)
    status_label.config(text=f"ESP32: {response}" if response else "No response")


for joint in joints:
    label = Label(slider_frame, text=joint, bg=BGcolor, fg="pink", font=("Arial", 11, "bold"))
    label.pack(pady=(10, 0))

    slider = Scale(
        slider_frame,
        from_=0,
        to=180,
        orient=HORIZONTAL,
        length=200,
        bg="red",
        fg="pink",
        troughcolor="black",
        highlightthickness=0,
    )
    slider.set(90)
    slider.pack()
    sliders[joint] = slider


status_label = Label(
    window, text="Ready", bg=BGcolor, fg="pink",
    font=("Arial", 10), wraplength=170, justify=LEFT, anchor="nw",
)


def record_pose():
    angles = [sliders[joint].get() for joint in joints]
    recorded.append(angles)
    status_label.config(text=f"Recorded position! {len(recorded)}: {angles}")


def clear_poses():
    recorded.clear()
    status_label.config(text="Cleared recording")


def save_poses():
    if not recorded:
        status_label.config(text="There's nothing to save!")
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
    )
    if not path:  
        return
    with open(path, "w") as f:
        json.dump({"joints": joints, "positions": recorded}, f, indent=2)
    status_label.config(text=f"Saved {len(recorded)} positions")


def load_poses():
    path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not path:
        return
    with open(path) as f:
        data = json.load(f)
    recorded.clear()
    recorded.extend(data["positions"])
    status_label.config(text=f"Loaded {len(recorded)} positions")


def play_poses():
    for i, angles in enumerate(recorded, start=1):
        status_label.config(text=f"Playing position {i}/{len(recorded)}")
        window.update()
        send(angles)
    status_label.config(text="Playback done")


def enable_controls():
    set_angles_button.config(state=NORMAL)
    play_button.config(state=NORMAL)


def disable_controls():
    set_angles_button.config(state=DISABLED)
    play_button.config(state=DISABLED)


def try_connect():
    
    global poll_job
    poll_job = None
    if simulation_mode:
        return
    if arm_control.connect():
        status_label.config(text="Connected to ESP32")
        enable_controls()
    else:
        disable_controls()
        status_label.config(text="Awaiting serial connection...")
        poll_job = window.after(1000, try_connect)


def toggle_mode():
    
    global simulation_mode, poll_job
    simulation_mode = not simulation_mode

   
    if poll_job is not None:
        window.after_cancel(poll_job)
        poll_job = None

    if simulation_mode:
        mode_button.config(text="I have a RoboArm!")
        enable_controls()
        status_label.config(text="Simulation Mode Activated")
    else:
        mode_button.config(text="I don't have a RoboArm!")
        disable_controls()
        try_connect()

def open_IKLibrary():
    open_ik_library(window, send_angles=send, is_simulation=lambda: simulation_mode)


set_angles_button = Button(window, text="Drive Servos", command=set_angles, font=("Arial", 12, "bold"), state=DISABLED)
play_button = Button(window, text="Play Recording", command=play_poses, state=DISABLED)
mode_button = Button(window, text="I don't have a RoboArm!", command=toggle_mode)


#middle
set_angles_button.place(x=300, y=20, width=180, height=40)
Button(window, text="Record Position", command=record_pose).place(x=300, y=80, width=180, height=35)
play_button.place(x=300, y=125, width=180, height=35)
Button(window, text="Save", command=save_poses).place(x=300, y=170, width=85, height=35)
Button(window, text="Load", command=load_poses).place(x=395, y=170, width=85, height=35)
Button(window, text="Clear", command=clear_poses).place(x=300, y=215, width=180, height=35)
mode_button.place(x=300, y=260, width=180, height=35)
status_label.place(x=300, y=305, width=180, height=55)

#right
Button(window, text="Open IK Library", command=open_IKLibrary).place(x=510, y=20, width=170, height=40)

window.after(100, try_connect)
window.mainloop() 