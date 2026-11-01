# Simple Worm Simulation

A cybersecurity educational simulation demonstrating how a network worm spreads across interconnected host computers using Breadth-First Search (BFS), taking into account host vulnerabilities, firewalls, and target file theft.

---

## 1. Network Topology

The network graph matches the layout below:

```
           [PC2] ----------------- [PC4]
          /                          |
         /                           |
   [PC1]                             |
         \                           |
          \                          |
           [PC3] ----------------- [PC5]
```

### Links (Undirected Connections):
- **PC1** connects to **PC2** and **PC3**
- **PC2** connects to **PC4** and **PC1**
- **PC3** connects to **PC5** and **PC1**
- **PC4** connects to **PC5** and **PC2**
- **PC5** connects to **PC4** and **PC3**

---

## 2. Host Profiles

| PC | Links | Vulnerable | Firewall | Files | Description |
|---|---|---|---|---|---|
| **PC1** | PC2, PC3 | True | False | `doc.txt`, `script.py` | Entry / standard node |
| **PC2** | PC1, PC4 | True | False | `report.txt`, `data.csv` | Intermediate node |
| **PC3** | PC1, PC5 | True | **True** | `important.txt` | **Firewall Enabled** (Blocks worm access) |
| **PC4** | PC2, PC5 | True | False | `test.py`, `photo.jpg` | Intermediate node |
| **PC5** | PC3, PC4 | **False** | False | `sample.txt` | **Not Vulnerable** (Patched system) |

**Target File Types:** `.txt`, `.py`, `.csv` (unsupported formats like `.jpg` are skipped).

---

## 3. Propagation Logic (BFS)

When the worm starts at a chosen PC (e.g. `PC1`):
1. **Infection of Initial Node**:
   - The starting PC is marked **INFECTED** (Green).
   - All files matching `.txt`, `.py`, `.csv` are stolen.
   - The starting PC is pushed to the BFS FIFO queue.
2. **Neighbor Scanning**:
   - Dequeue the next host (`current_pc`).
   - For each neighbor `target`:
     - **Already Infected**: Skipped (`[SKIP]`).
     - **Firewall Active (`firewall == True`)**: Blocked (`[BLOCKED]`). Edge & node colored Red.
     - **Not Vulnerable (`vulnerable == False`)**: Attack fails (`[FAILED]`). Edge & node colored Yellow.
     - **Vulnerable & Open**: The target is infected, target files are stolen, edge turns Green, and the target is added to the queue to spread further.
3. **Completion**:
   - The simulation finishes when all accessible nodes have been processed.
   - A final report summarizes: Infected PCs, Safe PCs, and total infected files.

---

## 4. How to Run

### Graphical Interface (Tkinter)
```bash
python "Worm GUI.py"
```

### Terminal Version
```bash
python "Worm With out GUI.py" PC1
```
or
```bash
python Worm.py
```
