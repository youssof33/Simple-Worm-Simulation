"""
==============================================================
 WORM PROPAGATION SIMULATOR - CONSOLE (NO GUI) VERSION
==============================================================

WHAT THIS PROGRAM DOES
----------------------
This is the same simulation as "warm with gui.py", but it runs
entirely in the terminal (no Tkinter window).

A fake worm starts on one PC and spreads through a small fakea
network. For every PC it reaches, it tries each directly linked
neighbour and decides what happens:

    * neighbour already infected  -> skip it
    * neighbour has a firewall    -> the worm is blocked
    * neighbour not vulnerable    -> the attack fails
    * otherwise                   -> the neighbour is infected,
                                     and added to the queue so
                                     the worm can spread from it

While infecting a PC, the worm also "steals" the files whose
extension is in TARGET_TYPES (.txt, .py, .csv) and skips the rest.

The order of infection is BREADTH-FIRST: all direct neighbours of
the current PC are tried before moving on to the PCs further away.
That is why a deque (double-ended queue) is used.

HOW TO RUN
----------
    python "warm with out gui .py"          -> asks for a start PC
    python "warm with out gui .py" PC3      -> starts on PC3 directly

NOTE: This is an educational simulation only. It does not touch
the real network or real files.
"""

import os      # used to enable ANSI colours on Windows terminals
import sys     # used to read an optional start PC from the command line
import time    # used for the small delays that make the spread visible
from collections import deque   # FIFO queue needed by the BFS algorithm


# ==============================================================
# 1. THE FAKE NETWORK
# ==============================================================
# "network" is a dictionary. Every key is a PC name, and every
# value is another dictionary describing that PC:
#
#   "links"      : list of PCs this PC is directly connected to
#   "vulnerable" : True  -> the worm can infect this PC
#                  False -> the worm cannot infect it
#   "firewall"   : True  -> the firewall blocks the worm completely
#   "files"      : list of file names stored on this PC
#
# The links are intentionally written both ways (PC1 -> PC2 and
# PC2 -> PC1) so the network can be scanned in any direction.
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
        "firewall": True,          # PC3 is protected by a firewall
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
        "vulnerable": False,       # PC5 is vulnerable-proof
        "firewall": False,
        "files": ["sample.txt"]
    }
}

# Only files with one of these extensions are "stolen" by the worm.
# Everything else (e.g. .jpg) is reported as skipped.
TARGET_TYPES = (".txt", ".py", ".csv")


# ==============================================================
# 2. TERMINAL COLOURS
# ==============================================================
# ANSI escape codes change the colour of terminal text.
# The pattern is: ESCAPE_CODE + text + RESET, where RESET puts the
# colour back to normal.
GREEN = "\033[92m"    # infections / successes
RED = "\033[91m"      # firewalls / blocks
YELLOW = "\033[93m"   # failures / warnings
BLUE = "\033[94m"     # section headers
GRAY = "\033[90m"     # secondary messages
BOLD = "\033[1m"      # bold text
RESET = "\033[0m"     # back to the default colour


def enable_ansi_on_windows():
    """
    Old Windows consoles ignore ANSI codes and print them as
    garbage. Calling `os.system("")` switches on virtual-terminal
    processing on Windows 10+, which makes the colours work.
    On Linux/macOS this does nothing harmful (it just runs an
    empty command), so the function is safe to call everywhere.
    """
    if os.name == "nt":          # "nt" means Windows
        os.system("")


# ==============================================================
# 3. SIMULATION STATE (reset before every run)
# ==============================================================
# infected_pcs   : set of PC names the worm has taken over.
#                  A set is used because we only need to know
#                  "is this PC already infected?" quickly.
# infected_files : flat list of "PC/file" strings the worm stole.
infected_pcs = set()
infected_files = []


def reset_state():
    """
    Clear the results of a previous run so the simulation always
    starts from a clean state. Without this, a second run would
    inherit the old infections.
    """
    infected_pcs.clear()
    infected_files.clear()


# ==============================================================
# 4. OUTPUT HELPERS
# ==============================================================
def log(message="", color=RESET):
    """
    Print one line in the requested colour.

    `color` is placed before the text and RESET after it, so the
    colour does not leak into the next print call.
    """
    print(f"{color}{message}{RESET}")


def animate_jump(src, dst, success):
    """
    Fake the "connection attempt" animation from the GUI version.

    It prints the source PC, then draws a dashed line one dash at
    a time (with a short sleep), and finally shows either an
    arrow (success) or an X (failure) followed by the target PC.

    `flush=True` forces Python to print immediately instead of
    buffering the output, which makes the animation visible.
    """
    print(f"\n  {src} ", end="", flush=True)

    for _ in range(6):              # draw six dashes
        print("-", end="", flush=True)
        time.sleep(0.15)            # 150 ms per dash

    symbol = ">" if success else " X"
    print(f"{symbol} {dst}")


def print_stats():
    """
    Print the same three numbers shown on the GUI dashboard:
    infected PCs, safe PCs and the number of stolen files.

    Safe PCs = every PC in the network minus the infected ones,
    so no extra bookkeeping is needed.
    """
    safe = len(network) - len(infected_pcs)
    print(
        f"{GRAY}  [stats] infected PCs: {GREEN}{len(infected_pcs)}{GRAY}"
        f" | safe PCs: {YELLOW}{safe}{GRAY}"
        f" | infected files: {BLUE}{len(infected_files)}{RESET}"
    )


# ==============================================================
# 5. INFECTING ONE PC
# ==============================================================
def infect(pc):
    """
    Mark a PC as infected and process its files.

    Steps:
      1. Add the PC to the infected set.
      2. Print an INFECTED message.
      3. For every file on that PC:
            - if the extension is in TARGET_TYPES -> steal it
            - otherwise                            -> skip it
    """
    infected_pcs.add(pc)
    log(f"{BOLD}{GREEN}[INFECTED] {pc}{RESET}")

    for file in network[pc]["files"]:
        # str.endswith() accepts a tuple, so this checks all three
        # extensions at once: .txt, .py and .csv.
        if file.endswith(TARGET_TYPES):
            infected_files.append(f"{pc}/{file}")   # remember the full path
            log(f"    File infected: {file}", GREEN)
        else:
            log(f"    File skipped : {file}", GRAY)


# ==============================================================
# 6. THE WORM: BREADTH-FIRST SEARCH (BFS)
# ==============================================================
def run_worm(start):
    """
    Spread the worm starting from `start` and print every step.

    The GUI version used one step per timer tick because Tkinter
    needs the window to stay responsive. In the console we can use
    a normal loop with time.sleep() instead - it does the same job
    and is much easier to follow.

    BFS works like this:
      - put the start PC in the queue
      - while the queue is not empty:
          take the PC at the FRONT (popleft -> first in, first out)
          try every neighbour of that PC
          every newly infected neighbour goes to the BACK of the queue

    That guarantees the closest PCs get infected before the PCs
    that are further away.
    """
    # Clean state for this run, then infect the chosen starting PC.
    reset_state()
    infect(start)

    # deque is the queue. It starts with only the start PC.
    queue = deque([start])

    while queue:                     # keep going while work is left
        current = queue.popleft()    # next PC whose neighbours we scan
        log(f"\n{BLUE}[SCAN] Checking neighbours of {current}...{RESET}")

        for target in network[current]["links"]:
            # --- Case 1: this neighbour was already infected ---------
            # Checking this first prevents infinite loops and avoids
            # printing the same infection twice.
            if target in infected_pcs:
                log(f"[SKIP] {target} already visited", GRAY)

            # --- Case 2: the neighbour has a firewall ----------------
            # The worm cannot pass, so the PC stays safe.
            elif network[target]["firewall"]:
                animate_jump(current, target, False)
                log(f"[BLOCKED] Firewall stopped access to {target}", RED)

            # --- Case 3: the neighbour is not vulnerable -------------
            # No firewall, but the system resists the attack.
            elif not network[target]["vulnerable"]:
                animate_jump(current, target, False)
                log(f"[FAILED] {target} is not vulnerable", YELLOW)

            # --- Case 4: the neighbour is open -----------------------
            # Connect, steal its files, and queue it up so the worm
            # can continue spreading from it later.
            else:
                animate_jump(current, target, True)
                log(f"[CONNECTED] {current} -> {target}", GREEN)
                infect(target)
                queue.append(target)     # add to the BACK of the queue

            # Show the running totals after every attempt, exactly
            # like the counters in the GUI dashboard.
            print_stats()

            # Small pause so the reader can follow the simulation.
            # 0.7 s matches the GUI's 700 ms timer delay.
            time.sleep(0.7)


# ==============================================================
# 7. FINAL REPORT
# ==============================================================
def final_report():
    """
    Print a summary after the queue is empty.

    safe_pcs uses set subtraction:
        set(network) - infected_pcs
    which leaves only the PCs that were never infected.
    sorted() makes the output stable and readable.
    """
    safe_pcs = sorted(set(network) - infected_pcs)

    log("\n========== FINAL REPORT ==========", BLUE)
    log(f"Infected PCs  : {sorted(infected_pcs)}", GREEN)
    log(f"Safe PCs      : {safe_pcs}", YELLOW)
    log(f"Infected files: {len(infected_files)}", GREEN)
    log("==================================", BLUE)


# ==============================================================
# 8. PROGRAM ENTRY POINT
# ==============================================================
def main():
    """
    Ask the user which PC should be infected first, validate the
    answer, run the simulation and print the report.
    """
    # Turn on colours for Windows terminals before printing anything.
    enable_ansi_on_windows()

    # Header, similar to the title of the GUI window.
    log("==================================================", GREEN)
    log("        WORM PROPAGATION SIMULATOR", BOLD + GREEN)
    log("     Cybersecurity Educational Dashboard", GRAY)
    log("==================================================", GREEN)

    # A start PC can be passed as a command-line argument, which is
    # handy for testing: python "warm with out gui .py" PC2
    if len(sys.argv) > 1:
        start = sys.argv[1].strip().upper()
        print(f"Starting PC (from argument): {start}")
    else:
        print("\nAvailable PCs:", ", ".join(network))
        start = input("Choose starting PC: ").strip().upper()

    # Validation: the choice must exist in the network dictionary.
    if start not in network:
        log(f"[ERROR] Unknown PC: {start!r}", RED)
        return                        # stop instead of crashing

    # Announce the run, then execute the BFS spread.
    log(f"\nStarting simulation from {start}...", BLUE)
    run_worm(start)

    # Everything is done -> summary.
    final_report()


# This guard makes the file safe to import: the simulation only
# runs when the file is executed directly, not when it is used as
# a module from another script.
if __name__ == "__main__":
    main()
