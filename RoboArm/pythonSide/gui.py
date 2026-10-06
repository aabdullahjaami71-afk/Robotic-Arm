from tkinter import *

window = Tk()

window.geometry("700x500")
window.title("RoboArm")

window.configure(bg="grey")

# -------------------- Sliders (left side) --------------------
joints = ["Base", "Shoulder", "Elbow", "Wrist", "Gripper"]

slider_frame = Frame(window, bg="grey")
slider_frame.place(x=20, y=20, width=250, height=460)

sliders = {}

for joint in joints:
    label = Label(slider_frame, text=joint, bg="grey", fg="white", font=("Arial", 11, "bold"))
    label.pack(pady=(10, 0))

    slider = Scale(
        slider_frame,
        from_=0,
        to=180,
        orient=HORIZONTAL,
        length=200,
        bg="grey",
        fg="white",
        troughcolor="white",
        highlightthickness=0,
    )
    slider.set(90)  # start centered
    slider.pack()
    sliders[joint] = slider

window.mainloop()