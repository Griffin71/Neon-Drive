# Neon City Drive

**Neon City Drive** is a fast-paced top-down open-world driving adventure built in Python using **Pygame**. Take on 20 story missions, manage cash, unlock weapons, and race through a neon-soaked city.

---

## ▶ Running the Game

### 1) Install requirements
```bash
pip install -r requirements.txt
```

### 2) Start the game
```bash
python main.py
```

---

## 🎮 Controls

| Action | Key |
|-------|-----|
| Accelerate | W |
| Brake / Reverse | S |
| Turn Left | A |
| Turn Right | D |
| Enter / Exit Vehicle | F |
| Mission Text / Dialogue Advance | SPACE |
| Interact (Shop) | E |
| Open Pause Menu | ESC |
| Open Radio Wheel | TAB |
| Open Weapon Wheel | Q |
| Save Game (in pause menu) | ENTER |

---

## 🧭 Gameplay Overview

- **Mission progression**: Complete missions one-by-one. After each mission completes, you must return to the safe house to receive the next briefing.
- **Currency**: Money is shown as **`R 12 500`** (Rand format). You start earning money beginning with mission 3.
- **Ammo Shop**: Visit the neon ammo store on the map and press **E** to purchase ammo.
- **Minimap**: Always visible. Shows safe house, gang house, ammo shop, mission target, and any active waypoint.
- **Save/Load**: There are **10 save slots**. Save your progress from the pause menu.
- **Police System**: The police will chase you when you commit crimes. The wanted level increases based on your criminal activity. Higher wanted levels spawn more police units. Avoid police or you'll be arrested and respawned at the hospital with a cash penalty.
  - **Wanted Levels**: 5-level system from low heat to maximum police presence
  - **Police Units**: Police vehicles and officers spawn based on your wanted level
  - **Heat Decay**: Crime heat gradually decreases over time (30+ seconds without crimes)
  - **Consequences**: Getting caught by police costs you cash and respawns you at the hospital

---

## 🖥️ System Requirements (PC Gamer)

### ✅ Minimum (Playable)
- **OS**: Windows 10 / macOS 10.15 / Linux (modern distro)
- **CPU**: Dual-core 2.0 GHz
- **RAM**: 4 GB
- **GPU**: Any graphics card that supports OpenGL 2.0+ (integrated GPUs are OK)
- **Storage**: 200 MB free disk space
- **Python**: 3.10 or newer

### 🚀 Recommended (Smooth Experience)
- **OS**: Windows 10/11, macOS 12+, or modern Linux
- **CPU**: Quad-core 3.0 GHz
- **RAM**: 8 GB+
- **GPU**: Discrete GPU or modern integrated graphics (OpenGL 3.3+ / DirectX 11 compatible)
- **Storage**: 500 MB free disk space
- **Python**: 3.10 or newer

---

## 🔧 Notes

- The game stores saves in the `saves/` folder.
- The game is built in Python with **pygame**, so performance depends on your CPU/GPU.

---

Enjoy the drive. Stay alive. Own the city.
