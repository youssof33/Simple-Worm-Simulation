import tkinter as tk
from tkinter import ttk
from collections import deque

# ================= NETWORK DATA =================

network = {
    "PC1": {
        "links": ["PC2", "PC3"],
        "vulnerable": True,
        "firewall": False,
        "files": ["doc.txt", "script.py"]
    },
    "PC2": {
        "links": ["PC1", "PC4"],
        "vulnerable": True,
        "firewall": False,
        "files": ["report.txt", "data.csv"]
    },
    "PC3": {
        "links": ["PC1", "PC5"],
        "vulnerable": True,
        "firewall": True,
        "files": ["important.txt"]
    },
    "PC4": {
        "links": ["PC2", "PC5"],
        "vulnerable": True,
        "firewall": False,
        "files": ["test.py", "photo.jpg"]
    },
    "PC5": {
        "links": ["PC3", "PC4"],
        "vulnerable": False,
        "firewall": False,
        "files": ["sample.txt"]
    }
}

TARGET_TYPES = (".txt", ".py", ".csv")

infected_pcs = set()
infected_files = []
queue = deque()

current_pc = None
neighbor_index = 0
running = False

# ================= COLORS =================

BG = "#111827"
PANEL = "#1F2937"
DARK = "#0B1220"
GREEN = "#22C55E"
RED = "#EF4444"
YELLOW = "#F59E0B"
BLUE = "#3B82F6"
WHITE = "#F9FAFB"
GRAY = "#9CA3AF"

# ================= WINDOW =================

root = tk.Tk()
root.title("Worm Propagation Simulator")
root.geometry("1150x780")
root.minsize(950, 680)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TCombobox",
    fieldbackground=PANEL,
    background=PANEL,
    foreground=WHITE
)

# ================= STATE =================

node_colors = {}

def reset_node_colors():
    for pc, data in network.items():
        if data["firewall"]:
            node_colors[pc] = RED
        elif not data["vulnerable"]:
            node_colors[pc] = YELLOW
        else:
            node_colors[pc] = BLUE

reset_node_colors()


# ================= LABEL HELPER =================

def make_label(parent, text, size=11, color=WHITE, bold=False):
    return tk.Label(
        parent,
        text=text,
        font=("Segoe UI", size, "bold" if bold else "normal"),
        bg=parent["bg"],
        fg=color
    )


# ================= HEADER =================

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=25, pady=(20, 12))

make_label(
    header,
    "WORM PROPAGATION SIMULATOR",
    23,
    GREEN,
    True
).pack(anchor="w")

make_label(
    header,
    "Cybersecurity Educational Dashboard | Fake Network",
    10,
    GRAY
).pack(anchor="w", pady=5)


# ================= STATISTICS =================

stats = tk.Frame(root, bg=BG)
stats.pack(fill="x", padx=20, pady=10)


def create_stat(parent, title, color):
    card = tk.Frame(
        parent,
        bg=PANEL,
        padx=15,
        pady=12
    )

    card.pack(
        side="left",
        expand=True,
        fill="x",
        padx=5
    )

    value = make_label(card, "0", 23, color, True)
    value.pack()

    make_label(card, title, 10, GRAY).pack()

    return value


infected_count = create_stat(stats, "INFECTED PCs", GREEN)
safe_count = create_stat(stats, "SAFE PCs", YELLOW)
file_count = create_stat(stats, "INFECTED FILES", BLUE)


def update_stats():
    infected_count.config(text=str(len(infected_pcs)))
    safe_count.config(text=str(len(network) - len(infected_pcs)))
    file_count.config(text=str(len(infected_files)))


# ================= MAIN CONTENT =================

content = tk.Frame(root, bg=BG)
content.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)

# ================= NETWORK PANEL =================

left = tk.Frame(
    content,
    bg=PANEL,
    padx=15,
    pady=15
)

left.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 10)
)

make_label(
    left,
    "NETWORK TOPOLOGY",
    13,
    WHITE,
    True
).pack(anchor="w", pady=(0, 10))


# ================= CONTROLS =================
# Controls are packed BEFORE the expanding canvas
# so they always remain visible.

controls = tk.Frame(left, bg=PANEL)
controls.pack(side="bottom", fill="x", pady=(12, 0))

make_label(
    controls,
    "Starting PC:",
    10,
    WHITE
).pack(side="left", padx=(0, 8))

start_var = tk.StringVar(value="PC1")

start_menu = ttk.Combobox(
    controls,
    textvariable=start_var,
    values=list(network.keys()),
    state="readonly",
    width=8
)

start_menu.pack(side="left", padx=5)


# ================= BUTTONS =================

start_button = tk.Button(
    controls,
    text="START SIMULATION",
    bg=GREEN,
    fg="white",
    activebackground="#16A34A",
    activeforeground="white",
    relief="flat",
    font=("Segoe UI", 9, "bold"),
    padx=15,
    pady=10
)

start_button.pack(side="left", padx=5)

reset_button = tk.Button(
    controls,
    text="RESET",
    bg="#374151",
    fg="white",
    activebackground="#4B5563",
    activeforeground="white",
    relief="flat",
    font=("Segoe UI", 9, "bold"),
    padx=18,
    pady=10
)

reset_button.pack(side="left", padx=5)


# ================= NETWORK CANVAS =================

canvas = tk.Canvas(
    left,
    bg=PANEL,
    highlightthickness=0,
    height=350
)

canvas.pack(
    fill="both",
    expand=True
)


def get_positions():
    width = max(canvas.winfo_width(), 400)
    height = max(canvas.winfo_height(), 300)

    return {
        "PC1": (width * 0.13, height * 0.25),
        "PC2": (width * 0.50, height * 0.25),
        "PC3": (width * 0.87, height * 0.25),
        "PC4": (width * 0.50, height * 0.75),
        "PC5": (width * 0.87, height * 0.75)
    }


def draw_network(event=None):
    canvas.delete("all")

    positions = get_positions()

    # Draw network connections

    for pc, data in network.items():
        x1, y1 = positions[pc]

        for target in data["links"]:
            if pc < target:
                x2, y2 = positions[target]

                canvas.create_line(
                    x1, y1,
                    x2, y2,
                    fill="#64748B",
                    width=3
                )

    # Draw PCs

    for pc, (x, y) in positions.items():

        color = node_colors[pc]

        canvas.create_oval(
            x - 35,
            y - 35,
            x + 35,
            y + 35,
            fill=color,
            outline=WHITE,
            width=2
        )

        canvas.create_text(
            x,
            y,
            text=pc,
            fill=WHITE,
            font=("Segoe UI", 12, "bold")
        )

        if pc in infected_pcs:
            status = "INFECTED"
        elif network[pc]["firewall"]:
            status = "FIREWALL"
        elif not network[pc]["vulnerable"]:
            status = "PROTECTED"
        else:
            status = "SAFE"

        canvas.create_text(
            x,
            y + 48,
            text=status,
            fill=color,
            font=("Segoe UI", 9, "bold")
        )


canvas.bind("<Configure>", draw_network)


# ================= RIGHT PANEL =================

right = tk.Frame(
    content,
    bg=PANEL,
    width=300,
    padx=12,
    pady=12
)

right.pack(side="right", fill="both")
right.pack_propagate(False)

make_label(
    right,
    "SIMULATION LOG",
    13,
    WHITE,
    True
).pack(anchor="w", pady=5)


log_box = tk.Text(
    right,
    bg=DARK,
    fg=WHITE,
    font=("Consolas", 9),
    relief="flat",
    wrap="word",
    state="disabled"
)

log_box.pack(
    fill="both",
    expand=True,
    pady=8
)


def log(message, color=WHITE):
    log_box.config(state="normal")

    tag = str(color)

    log_box.tag_config(tag, foreground=color)
    log_box.insert("end", message + "\n", tag)

    log_box.see("end")
    log_box.config(state="disabled")


# ================= FILE DISPLAY =================

make_label(
    right,
    "SELECTED FILES",
    11,
    WHITE,
    True
).pack(anchor="w", pady=5)

file_list = tk.Listbox(
    right,
    bg=DARK,
    fg=GREEN,
    font=("Consolas", 9),
    height=7,
    relief="flat",
    selectbackground="#374151"
)

file_list.pack(fill="x", pady=5)


def show_files(pc):
    file_list.delete(0, "end")

    for file in network[pc]["files"]:
        if file.endswith(TARGET_TYPES):
            file_list.insert(
                "end",
                f"{pc}/{file} - Selected"
            )
        else:
            file_list.insert(
                "end",
                f"{pc}/{file} - Skipped"
            )


# ================= STATUS FOOTER =================

footer = tk.Frame(root, bg=BG)
footer.pack(fill="x", padx=25, pady=12)

status_label = make_label(
    footer,
    "Ready to simulate",
    10,
    GRAY
)

status_label.pack(side="left")

make_label(
    footer,
    "Educational Use Only",
    9,
    GRAY
).pack(side="right")


# ================= INFECTION DISPLAY =================

def infect(pc):
    infected_pcs.add(pc)
    node_colors[pc] = GREEN

    log(f"[INFECTED] {pc}", GREEN)

    for file in network[pc]["files"]:

        if file.endswith(TARGET_TYPES):
            infected_files.append(f"{pc}/{file}")
            log(f"  File selected: {file}", GREEN)
        else:
            log(f"  File skipped: {file}", GRAY)

    show_files(pc)
    update_stats()
    draw_network()


# ================= START SIMULATION =================

def start_simulation():

    global current_pc, neighbor_index, running

    if running:
        return

    start = start_var.get()

    infected_pcs.clear()
    infected_files.clear()
    queue.clear()

    reset_node_colors()

    current_pc = None
    neighbor_index = 0

    log_box.config(state="normal")
    log_box.delete("1.0", "end")
    log_box.config(state="disabled")

    file_list.delete(0, "end")

    running = True

    start_button.config(state="disabled")
    start_menu.config(state="disabled")

    status_label.config(
        text="Simulation running...",
        fg=YELLOW
    )

    log("========== SIMULATION STARTED ==========", BLUE)
    log(f"Starting PC: {start}", BLUE)

    infect(start)
    queue.append(start)

    root.after(500, process_next)


# ================= BFS SIMULATION =================

def process_next():

    global current_pc, neighbor_index

    if not queue:
        finish_simulation()
        return

    if current_pc is None:
        current_pc = queue.popleft()
        neighbor_index = 0

        log(f"\n[SCAN] Checking {current_pc}...", BLUE)

    links = network[current_pc]["links"]

    if neighbor_index >= len(links):
        current_pc = None
        root.after(500, process_next)
        return

    target = links[neighbor_index]
    neighbor_index += 1

    if target in infected_pcs:

        log(f"[SKIP] {target} already visited", GRAY)

    elif network[target]["firewall"]:

        node_colors[target] = RED

        log(
            f"[BLOCKED] {target}: Firewall enabled",
            RED
        )

        draw_network()

    elif not network[target]["vulnerable"]:

        node_colors[target] = YELLOW

        log(
            f"[FAILED] {target}: Not vulnerable",
            YELLOW
        )

        draw_network()

    else:

        log(
            f"[CONNECTED] {current_pc} -> {target}",
            GREEN
        )

        infect(target)
        queue.append(target)

    root.after(700, process_next)


# ================= FINAL REPORT =================

def finish_simulation():

    global running, current_pc

    running = False
    current_pc = None

    safe = sorted(set(network) - infected_pcs)

    log("\n========== FINAL REPORT ==========", BLUE)
    log(f"Infected PCs: {sorted(infected_pcs)}", GREEN)
    log(f"Safe PCs: {safe}", YELLOW)
    log(f"Infected files: {len(infected_files)}", GREEN)
    log("==================================", BLUE)

    update_stats()

    status_label.config(
        text="Simulation completed",
        fg=GREEN
    )

    start_button.config(state="normal")
    start_menu.config(state="readonly")


# ================= RESET SIMULATION =================

def reset_simulation():

    global current_pc, neighbor_index

    if running:
        return

    infected_pcs.clear()
    infected_files.clear()
    queue.clear()

    current_pc = None
    neighbor_index = 0

    reset_node_colors()

    log_box.config(state="normal")
    log_box.delete("1.0", "end")
    log_box.config(state="disabled")

    file_list.delete(0, "end")

    status_label.config(
        text="Ready to simulate",
        fg=GRAY
    )

    update_stats()
    draw_network()


# ================= BUTTON COMMANDS =================

start_button.config(command=start_simulation)
reset_button.config(command=reset_simulation)


# ================= RUN APPLICATION =================

update_stats()

root.after(300, draw_network)

root.mainloop()