from collections import deque
import time

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

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def animate_jump(src, dst, success):
    print(f"\n  {src} ", end="", flush=True)

    for _ in range(6):
        print("-", end="", flush=True)
        time.sleep(0.15)

    symbol = ">" if success else " X"
    print(f"{symbol} {dst}")


def infect(pc):
    infected_pcs.add(pc)
    print(f"{GREEN}[INFECTED] {pc}{RESET}")

    for file in network[pc]["files"]:
        if file.endswith(TARGET_TYPES):
            infected_files.append(f"{pc}/{file}")
            print(f"    File infected: {file}")
        else:
            print(f"    File skipped: {file}")


def run_worm(start):
    infected_pcs.clear()
    infected_files.clear()

    infect(start)
    queue = deque([start])

    while queue:
        current = queue.popleft()
        print(f"\n[SCAN] Checking neighbours of {current}...")

        for target in network[current]["links"]:

            if target in infected_pcs:
                print(f"[SKIP] {target} already visited")

            elif network[target]["firewall"]:
                animate_jump(current, target, False)
                print(f"{YELLOW}[BLOCKED] Firewall stopped access to {target}{RESET}")

            elif not network[target]["vulnerable"]:
                animate_jump(current, target, False)
                print(f"{YELLOW}[FAILED] {target} is not vulnerable{RESET}")

            else:
                animate_jump(current, target, True)
                infect(target)
                queue.append(target)
                time.sleep(0.8)


def main():
    print("Available PCs:", ", ".join(network))

    start = input("Choose starting PC: ").strip().upper()

    if start not in network:
        print("[ERROR] Unknown PC.")
        return

    run_worm(start)

    safe_pcs = sorted(set(network) - infected_pcs)

    print("\n========== FINAL REPORT ==========")
    print("Infected PCs  :", sorted(infected_pcs))
    print("Safe PCs      :", safe_pcs)
    print("Infected files:", len(infected_files))
    print("==================================")


if __name__ == "__main__":
    main()