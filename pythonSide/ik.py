from tkinter import *

BGcolor = "darkred"

# set when the window opens, used by question_library
_send = None
_is_simulation = lambda: False
_result_label = None


def question_library(is_correct, angles=None, correct_msg="Nice, Correct!", wrong_msg="Try again!"):
    if not is_correct:
        _result_label.config(text=wrong_msg)
        return

    if _is_simulation():
        _result_label.config(text=f"{correct_msg} (simulation mode)")
    elif _send and angles:
        _result_label.config(text=f"{correct_msg} Driving servos...")
        _result_label.update()
        response = _send(angles)
        _result_label.config(text=f"{correct_msg} ESP32: {response}" if response else f"{correct_msg} No response from arm")
    else:
        _result_label.config(text=correct_msg)


# ---- questions: one function each ----

def question_1(answer):
    # Q: reach of a fully extended 2-link arm with L1=10 and L2=8?
    try:
        is_correct = float(answer) == 18
    except ValueError:
        is_correct = False
    question_library(is_correct, angles=[90, 90, 90, 90, 90])  # order: Gripper, Wrist, Shoulder, Elbow, Base


def question_2(answer):
    # copy this pattern for each new question
    question_library(answer.strip().lower() == "elbow", angles=[90, 45, 90, 120, 90])


# ---- window ----

def build_question(win, prompt, check_fn):
    Label(win, text=prompt, bg=BGcolor, fg="pink", font=("Arial", 11), wraplength=600).pack(pady=(15, 0))
    entry = Entry(win)
    entry.pack(pady=5)
    Button(win, text="Submit", command=lambda: check_fn(entry.get())).pack()


def open_ik_library(parent, send_angles=None, is_simulation=None):
    """Builds the IK Library window as a child of `parent`."""
    global _send, _is_simulation, _result_label
    _send = send_angles
    _is_simulation = is_simulation or (lambda: False)

    win = Toplevel(parent)
    win.title("IK Library")
    win.geometry("700x500")
    win.configure(bg=BGcolor)

    Label(win, text="IK Library", bg=BGcolor, fg="pink",
          font=("Arial", 14, "bold")).pack(pady=10)

    build_question(win, "Q1: Reach of a fully extended 2-link arm with L1=10 and L2=8?", question_1)
    build_question(win, "Q2: Which joint changes the distance between the wrist and shoulder?", question_2)

    _result_label = Label(win, text="", bg=BGcolor, fg="pink", font=("Arial", 11, "bold"), wraplength=600)
    _result_label.pack(pady=20)

    return win