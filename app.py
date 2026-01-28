import tkinter as tk
from tkinter import scrolledtext
import main as backend

def main():
    root = tk.Tk()
    root.title("kcalendar")
    root.geometry("800x500")

    output = scrolledtext.ScrolledText(
        root,
        wrap="word",
        state="disabled",
        font=("Consolas", 10)
    )
    output.pack(fill="both", expand=True, padx=8, pady=(8, 4))

    entry = tk.Entry(root, font=("Consolas", 10))
    entry.pack(fill="x", padx=8, pady=(0, 8))
    entry.focus()

    waiting_for_input = False
    input_value = None

    def write_line(text):
        output.configure(state="normal")
        output.insert("end", text + "\n")
        output.see("end")
        output.configure(state="disabled")

    def on_enter(event=None):
        nonlocal waiting_for_input, input_value

        text = entry.get()
        entry.delete(0, "end")

        # If backend is waiting for a response to app_input(...)
        if waiting_for_input:
            input_value = text
            waiting_for_input = False
            return

        # Otherwise treat it like a normal command line (we'll hook handle_command later)
        if text.strip():
            write_line("> " + text.strip())
    entry.bind("<Return>", on_enter)
    
    def gui_print(text):
        write_line(str(text))
    backend.app_print = gui_print
    backend.app_print("GUI gooked to backend app_print :)")

    def gui_input(prompt):
        nonlocal waiting_for_input, input_value

        # show prompt in output
        write_line(str(prompt))
        entry.focus()
        # set waiting state and block until user enters something
        waiting_for_input = True
        input_value = None

        # keep the UI responsive while waiting
        while waiting_for_input:
            root.update()

        return input_value
    
    backend.app_input = gui_input
    backend.main_loop()
    
    

    

    write_line("kcalendar GUI — terminal mode")
    root.mainloop()

if __name__ == "__main__":
    main()