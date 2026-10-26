from tkinter import *
from tkinter import filedialog
import arm_control
import json
from ik import open_ik_library
from build import open_build_instructions

BGcolor = "darkred"

simulation_mode = False   
poll_job = None     

window = Tk()
window.geometry("700x500")
window.minsize(560, 460)
window.title("RoboArm")
window.configure(bg=BGcolor)

joints = ["Gripper", "Wrist", "Shoulder", "Elbow", "Base"]


window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=3)
window.columnconfigure(1, weight=2)
window.columnconfigure(2, weight=2)

left = Frame(window, bg=BGcolor)
left.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
left.rowconfigure(0, weight=1)
left.columnconfigure(0, weight=1)

middle = Frame(window, bg=BGcolor)
middle.grid(row=0, column=1, sticky="nsew", padx=10, pady=20)
middle.columnconfigure(0, weight=1)
for r in range(6):
    middle.rowconfigure(r, weight=1, uniform="buttons")
middle.rowconfigure(6, weight=2)

right = Frame(window, bg=BGcolor)
right.grid(row=0, column=2, sticky="nsew", padx=(10, 20), pady=20)
right.columnconfigure(0, weight=1)

slider_frame = Frame(left, bg=BGcolor)
slider_frame.grid(row=0, column=0, sticky="nsew")
slider_frame.columnconfigure(0, weight=1)

sliders = {}
recorded = []


flipped_joints = {"Elbow"}


#mechanically, the elbow joint is flipped so we need this to fix it
def apply_flips(angles):
    return [180 - a if joint in flipped_joints else a
            for joint, a in zip(joints, angles)]


def send(angles):
    if simulation_mode:
        return "simulation_mode"
    return arm_control.send_angles(apply_flips(angles))


def set_angles():
    angles = [sliders[joint].get() for joint in joints]
    status_label.config(text="Sweeping...")
    window.update()

    response = send(angles)
    status_label.config(text=f"ESP32: {response}" if response else "No response")


for i, joint in enumerate(joints):
    slider_frame.rowconfigure(i, weight=1)
    block = Frame(slider_frame, bg=BGcolor)
    block.grid(row=i, column=0, sticky="ew")

    label = Label(block, text=joint, bg=BGcolor, fg="pink", font=("Arial", 11, "bold"))
    label.pack()

    slider = Scale(
        block,
        from_=0,
        to=180,
        orient=HORIZONTAL,
        bg="red",
        fg="pink",
        troughcolor="black",
        highlightthickness=0,
    )
    slider.set(90)
    slider.pack(fill=X)   # stretches with the window
    sliders[joint] = slider


status_label = Label(
    middle, text="Ready", bg=BGcolor, fg="pink",
    font=("Arial", 10), wraplength=150, justify=LEFT, anchor="nw",
)

status_label.bind("<Configure>", lambda e: status_label.config(wraplength=max(e.width - 6, 50)))


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


def open_buildInstructions():
    open_build_instructions(window)


set_angles_button = Button(middle, text="Drive Servos", command=set_angles, font=("Arial", 12, "bold"), state=DISABLED)
play_button = Button(middle, text="Play Recording", command=play_poses, state=DISABLED)
mode_button = Button(middle, text="I don't have a RoboArm!", command=toggle_mode)


#left
#Button(left, text="Build Instructions", command=open_buildInstructions).grid(
   # row=1, column=0, sticky="ew", pady=(10, 0), ipady=6)

#middle
PAD = dict(sticky="nsew", pady=4)
set_angles_button.grid(row=0, column=0, **PAD)
Button(middle, text="Record Position", command=record_pose).grid(row=1, column=0, **PAD)
play_button.grid(row=2, column=0, **PAD)

save_load = Frame(middle, bg=BGcolor)
save_load.grid(row=3, column=0, **PAD)
save_load.rowconfigure(0, weight=1)
save_load.columnconfigure(0, weight=1)
save_load.columnconfigure(1, weight=1)
Button(save_load, text="Save", command=save_poses).grid(row=0, column=0, sticky="nsew", padx=(0, 4))
Button(save_load, text="Load", command=load_poses).grid(row=0, column=1, sticky="nsew", padx=(4, 0))

Button(middle, text="Clear", command=clear_poses).grid(row=4, column=0, **PAD)
mode_button.grid(row=5, column=0, **PAD)
status_label.grid(row=6, column=0, sticky="nsew", pady=(8, 0))

#right
Button(right, text="Open IK Library", command=open_IKLibrary).grid(
    row=0, column=0, sticky="ew", ipady=10)

window.after(100, try_connect)
window.mainloop()