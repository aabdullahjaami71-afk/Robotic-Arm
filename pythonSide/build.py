from tkinter import *
import os

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

BGcolor = "darkred"

SLIDES = [
    {
        "title": "Step 1: Parts List",
        "description": "Gather everything you need: servos, Arduino/ESP32, wiring, power supply, and the printed arm parts.",
        "image": "build_images/step1.png",
    },
    {
        "title": "Step 2: Assemble the Base",
        "description": "Mount the base servo to the base plate and secure it with screws.",
        "image": "build_images/step2.png",
    },
    {
        "title": "Step 3: Shoulder and Elbow",
        "description": "Attach the shoulder and elbow servos. Remember the elbow is mounted flipped.",
        "image": "build_images/step3.png",
    },
    {
        "title": "Step 4: Wrist and Gripper",
        "description": "Install the wrist servo and gripper at the end of the arm.",
        "image": "build_images/step4.png",
    },
    {
        "title": "Step 5: Wiring",
        "description": "Connect each servo signal wire to the board, then connect power and ground.",
        "image": "build_images/step5.png",
    },
]

IMG_MAX_W = 520
IMG_MAX_H = 280

_window = None  # keeps track of the open window so we don't open two


def _load_image(path):
    """Returns a PhotoImage or None."""
    if not path:
        return None
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    if not os.path.exists(path):
        return None
    try:
        if HAS_PIL:
            img = Image.open(path)
            img.thumbnail((IMG_MAX_W, IMG_MAX_H))
            return ImageTk.PhotoImage(img)
        return PhotoImage(file=path)
    except Exception:
        return None


def open_build_instructions(parent, slides=None):
    global _window

    if _window is not None and _window.winfo_exists():
        _window.lift()
        _window.focus_force()
        return

    slides = slides or SLIDES
    if not slides:
        return

    win = Toplevel(parent)
    _window = win
    win.title("Build Instructions")
    win.geometry("640x520")
    win.configure(bg=BGcolor)
    win.resizable(False, False)

    state = {"index": 0, "photo": None}

    title_label = Label(win, bg=BGcolor, fg="pink", font=("Arial", 16, "bold"))
    title_label.pack(pady=(15, 5))

    image_frame = Frame(win, bg="black", width=IMG_MAX_W + 10, height=IMG_MAX_H + 10)
    image_frame.pack(pady=5)
    image_frame.pack_propagate(False)
    image_label = Label(image_frame, bg="black", fg="gray", font=("Arial", 11))
    image_label.pack(expand=True)

    desc_label = Label(
        win, bg=BGcolor, fg="white", font=("Arial", 12),
        wraplength=560, justify=CENTER,
    )
    desc_label.pack(pady=10, padx=20)

    nav = Frame(win, bg=BGcolor)
    nav.pack(side=BOTTOM, pady=15)

    prev_button = Button(nav, text="\u25C0", font=("Arial", 14, "bold"), width=4)
    counter_label = Label(nav, bg=BGcolor, fg="pink", font=("Arial", 11), width=10)
    next_button = Button(nav, text="\u25B6", font=("Arial", 14, "bold"), width=4)
    prev_button.pack(side=LEFT, padx=10)
    counter_label.pack(side=LEFT)
    next_button.pack(side=LEFT, padx=10)

    def show():
        slide = slides[state["index"]]
        title_label.config(text=slide.get("title", ""))
        desc_label.config(text=slide.get("description", ""))

        photo = _load_image(slide.get("image"))
        state["photo"] = photo  # keep a reference or tkinter garbage collects it
        if photo:
            image_label.config(image=photo, text="")
        else:
            image_label.config(image="", text="(no image)")

        counter_label.config(text=f"{state['index'] + 1} / {len(slides)}")
        prev_button.config(state=NORMAL if state["index"] > 0 else DISABLED)
        next_button.config(state=NORMAL if state["index"] < len(slides) - 1 else DISABLED)

    def go_prev(event=None):
        if state["index"] > 0:
            state["index"] -= 1
            show()

    def go_next(event=None):
        if state["index"] < len(slides) - 1:
            state["index"] += 1
            show()

    prev_button.config(command=go_prev)
    next_button.config(command=go_next)
    win.bind("<Left>", go_prev)
    win.bind("<Right>", go_next)
    win.focus_set()

    show()