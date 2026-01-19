import tkinter as tk
from tkinter import ttk


def round_to_multiple(value, multiple):
    if value < 0:
        return -(round(-value / multiple) * multiple)
    else:
        return round(value / multiple) * multiple

def calculate_other_side(given_value, ratio_num, ratio_den, is_width=True):
    if given_value <= 0:
        return 0
    if is_width:
        other_val = given_value * ratio_den / ratio_num
    else:
        other_val = given_value * ratio_num / ratio_den
    return int(round_to_multiple(other_val, 8))

def update_calculations(*args):
    try:
        ratio_str = ratio_var.get()
        if ":" not in ratio_str:
            return
        num, den = map(int, ratio_str.split(":"))

        focus_widget = root.focus_get()
        width_raw = width_var.get()
        height_raw = height_var.get()

        updated_by_user_input = False
        if focus_widget == width_entry or focus_widget == width_up_btn or focus_widget == width_down_btn:
            if width_raw:
                w_val = int(width_raw)
                rounded_w = int(round_to_multiple(w_val, 8))
                width_var.set(str(rounded_w))
                calculated_h = calculate_other_side(rounded_w, num, den, is_width=True)
                height_var.set(str(calculated_h))
                updated_by_user_input = True
        elif focus_widget == height_entry or focus_widget == height_up_btn or focus_widget == height_down_btn:
            if height_raw:
                h_val = int(height_raw)
                rounded_h = int(round_to_multiple(h_val, 8))
                height_var.set(str(rounded_h))
                calculated_w = calculate_other_side(rounded_h, num, den, is_width=False)
                width_var.set(str(calculated_w))
                updated_by_user_input = True
        if not updated_by_user_input and width_raw and height_raw:
            try:
                w_val = int(width_var.get())
                calculated_h_from_w = calculate_other_side(w_val, num, den, is_width=True)
                height_var.set(str(calculated_h_from_w))
            except ValueError:
                pass

        update_visualization(num, den)

        update_reference_resolutions(num, den)

    except ValueError:
        pass

def update_visualization(ratio_num, ratio_den):
    canvas.delete("all")
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    if canvas_width <= 1 or canvas_height <= 1:
        canvas_width = CANVAS_SIZE[0]
        canvas_height = CANVAS_SIZE[1]

    max_rect_width = canvas_width * 0.9
    max_rect_height = canvas_height * 0.9

    rect_width = max_rect_width
    rect_height = rect_width * ratio_den / ratio_num

    if rect_height > max_rect_height:
        rect_height = max_rect_height
        rect_width = rect_height * ratio_num / ratio_den

    x_start = (canvas_width - rect_width) / 2
    y_start = (canvas_height - rect_height) / 2
    x_end = x_start + rect_width
    y_end = y_start + rect_height

    canvas.create_rectangle(x_start, y_start, x_end, y_end, outline="black", width=2, fill="#f0f0f0")
    
    current_width = width_var.get() or "0"
    current_height = height_var.get() or "0"
    resolution_text = f"{current_width} x {current_height}\n({ratio_num}:{ratio_den})"
    center_x = (x_start + x_end) / 2
    center_y = (y_start + y_end) / 2
    canvas.create_text(center_x, center_y, text=resolution_text, fill="dark blue", font=("Arial", 10), justify='center')

def update_reference_resolutions(ratio_num, ratio_den):
    listbox.delete(0, tk.END)
    
    horizontal_resolutions = {
        (4, 3): [(800, 600), (1024, 768), (1280, 960), (1400, 1050), (1600, 1200), (2048, 1536)],
        (16, 9): [(1280, 720), (1366, 768), (1600, 900), (1920, 1080), (2560, 1440), (3840, 2160), (7680, 4320)],
        (21, 9): [(2560, 1080), (3440, 1440), (5120, 2160)],
        (18, 9): [(2160, 1080), (2220, 1125), (2880, 1440), (3840, 1920)]
    }
    
    vertical_resolutions = {
        (9, 16): [(720, 1280), (768, 1366), (900, 1600), (1080, 1920), (1440, 2560), (2160, 3840), (4320, 7680)],
        (3, 4): [(600, 800), (768, 1024), (960, 1280), (1050, 1400), (1200, 1600), (1536, 2048)],
        (9, 21): [(1080, 2560), (1440, 3440), (2160, 5120)],
        (9, 18): [(1080, 2160), (1125, 2220), (1440, 2880), (1920, 3840)]
    }

    if (ratio_num, ratio_den) in horizontal_resolutions:
        resolutions = horizontal_resolutions[(ratio_num, ratio_den)]
        category_label = "Горизонтальные:"
    elif (ratio_num, ratio_den) in vertical_resolutions:
        resolutions = vertical_resolutions[(ratio_num, ratio_den)]
        category_label = "Вертикальные:"
    else:
        resolutions = []
        category_label = "Стандарты:"

    listbox.insert(tk.END, category_label)
    listbox.itemconfig(listbox.size()-1, {'fg': 'gray'})
    for res in resolutions:
        listbox.insert(tk.END, f"{res[0]} x {res[1]}")

def on_ratio_change(event):
    update_calculations()

def increment_dimension(var, step):
    try:
        current_val = int(var.get())
    except ValueError:
        current_val = 0
    new_val = current_val + step
    if new_val < 0:
        new_val = 0
    var.set(str(new_val))
    
    update_calculations()

def copy_text_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update() 

def create_context_menu(entry_widget):
    menu = tk.Menu(entry_widget, tearoff=0)
    menu.add_command(label="Копировать", command=lambda: copy_text_to_clipboard(entry_widget.get()))
    return menu

def show_context_menu(event, menu):
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

def bind_copy_shortcut(entry_widget):
    def on_ctrl_c(event):
        copy_text_to_clipboard(entry_widget.get())
        return "break" 
    entry_widget.bind("<Control-c>", on_ctrl_c)
    entry_widget.bind("<Control-C>", on_ctrl_c) 

CANVAS_SIZE = (250, 200)

root = tk.Tk()
root.title("Калькулятор пропорций")
root.geometry("750x400")

ratio_var = tk.StringVar(value="16:9")
width_var = tk.StringVar(value="1920")
height_var = tk.StringVar(value="1080")

left_frame = tk.Frame(root, padx=10, pady=10)
left_frame.pack(side=tk.LEFT, fill=tk.Y, anchor="nw")

right_frame = tk.Frame(root, padx=5, pady=10)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

tk.Label(left_frame, text="Соотношение сторон:").pack(anchor="w")
ratio_combo = ttk.Combobox(
    left_frame, 
    textvariable=ratio_var, 
    values=["4:3", "16:9", "18:9", "21:9", "3:4", "9:16", "9:18", "21:9"],
    state="readonly",
    width=10
)
ratio_combo.pack(pady=(0, 10), anchor="w")
ratio_combo.bind("<<ComboboxSelected>>", on_ratio_change)

input_frame = tk.Frame(left_frame)
input_frame.pack(fill=tk.X, pady=(0, 10))

tk.Label(input_frame, text="Width:").grid(row=0, column=0, sticky="w")
width_frame = tk.Frame(input_frame)
width_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
width_down_btn = tk.Button(width_frame, text="-8", width=3, command=lambda: increment_dimension(width_var, -8))
width_down_btn.pack(side=tk.LEFT)
width_entry = tk.Entry(width_frame, textvariable=width_var, width=10)
width_entry.pack(side=tk.LEFT, padx=(2, 2))
width_up_btn = tk.Button(width_frame, text="+8", width=3, command=lambda: increment_dimension(width_var, 8))
width_up_btn.pack(side=tk.LEFT)

tk.Label(input_frame, text="Height:").grid(row=1, column=0, sticky="w", pady=(5, 0))
height_frame = tk.Frame(input_frame)
height_frame.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))
height_down_btn = tk.Button(height_frame, text="-8", width=3, command=lambda: increment_dimension(height_var, -8))
height_down_btn.pack(side=tk.LEFT)
height_entry = tk.Entry(height_frame, textvariable=height_var, width=10)
height_entry.pack(side=tk.LEFT, padx=(2, 2))
height_up_btn = tk.Button(height_frame, text="+8", width=3, command=lambda: increment_dimension(height_var, 8))
height_up_btn.pack(side=tk.LEFT)

width_context_menu = create_context_menu(width_entry)
height_context_menu = create_context_menu(height_entry)


width_entry.bind("<Button-3>", lambda e: show_context_menu(e, width_context_menu))
height_entry.bind("<Button-3>", lambda e: show_context_menu(e, height_context_menu))

bind_copy_shortcut(width_entry)
bind_copy_shortcut(height_entry)

for entry in [width_entry, height_entry]:
    entry.bind("<FocusOut>", lambda e: update_calculations())
    entry.bind("<Return>", lambda e: update_calculations())


canvas_frame = tk.LabelFrame(right_frame, text="Визуализация", padx=5, pady=5)
canvas_frame.pack(fill=tk.X, pady=(0, 10))

canvas = tk.Canvas(canvas_frame, bg='white', width=CANVAS_SIZE[0], height=CANVAS_SIZE[1])
canvas.pack()

ref_frame = tk.LabelFrame(right_frame, text="Стандартные разрешения", padx=5, pady=5)
ref_frame.pack(fill=tk.BOTH, expand=True)

listbox = tk.Listbox(ref_frame)
listbox.pack(fill=tk.BOTH, expand=True)

update_calculations()

root.mainloop()