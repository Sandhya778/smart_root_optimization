# 🗺️ Smart Route Optimizer — Gwalior

> **Intelligent delivery and travel route planning using Nearest-Neighbor heuristic + 2-opt optimization.**
> No external map APIs required. Runs fully offline.

---

## 📌 Project Overview

Smart Route Optimizer is a lightweight, dependency-free route planning tool built for **Gwalior City (474011), Madhya Pradesh**. It finds the shortest round-trip path through a set of stops using a two-stage algorithm: a fast **Nearest-Neighbor greedy search** followed by **2-opt local improvement**. It ships with both a command-line interface and a browser-based interactive UI.

| Component | File | Description |
|---|---|---|
| Core Algorithm | `route_optimizer.py` | Python CLI — full optimization engine |
| Web Interface | `route_optimizer_ui.html` | Browser UI — canvas map + live ETA table |
| Sample Data | `stops.csv` | 9 real Gwalior stops with GPS coordinates |

---

## 📁 Project Structure

```
smart-route-optimizer/
│
├── route_optimizer.py       # Main Python optimizer (CLI)
├── route_optimizer_ui.html  # Interactive browser-based UI
├── stops.csv                # Sample stops — Gwalior City
└── README.md                # This file
```

---

## ⚙️ Algorithm

The optimizer uses a **two-phase approach**:

### Phase 1 — Nearest-Neighbor Heuristic
Builds an initial route by always visiting the closest unvisited stop. Multiple random starting points are tried and the best is kept.

### Phase 2 — 2-opt Improvement
Iteratively reverses sub-segments of the route to eliminate crossing paths. Continues until no further improvement is found or the time limit (5 seconds) is reached.

### Distance Calculation
All distances use the **Haversine formula** — great-circle distance between two GPS coordinates:

```
d = 2R · arcsin(√(sin²(Δlat/2) + cos(lat₁)·cos(lat₂)·sin²(Δlon/2)))
```

where R = 6371 km (Earth's radius).

### Complexity
| Step | Time Complexity |
|---|---|
| Distance matrix build | O(n²) |
| Nearest-Neighbor | O(n²) |
| 2-opt (one pass) | O(n²) |
| Total (typical) | O(n² · iterations) |

---

## 🚀 Getting Started

### Requirements

- Python **3.8+**
- No external libraries required — uses only Python standard library (`math`, `csv`, `argparse`, `itertools`, `random`, `time`)

### Installation

```bash
# Clone or download the project
git clone https://github.com/yourname/smart-route-optimizer.git
cd smart-route-optimizer
```

No `pip install` needed. ✅

---

## 💻 Usage — Python CLI

### 1. Demo Mode (Gwalior built-in stops)
```bash
python route_optimizer.py
```
Runs with 9 pre-loaded Gwalior City stops.

### 2. Load from CSV File
```bash
python route_optimizer.py --file stops.csv
```

### 3. Interactive Mode (Enter stops manually)
```bash
python route_optimizer.py --interactive
```
You will be prompted to enter stop name, latitude, and longitude one by one.

### 4. Custom Speed & Depot
```bash
python route_optimizer.py --file stops.csv --speed 40 --depot "Gwalior Junction Station"
```

### All CLI Options

| Flag | Default | Description |
|---|---|---|
| `--file CSV` | — | Load stops from a CSV file |
| `--interactive` | off | Manually enter stops in terminal |
| `--speed KMH` | 30 | Average travel speed for ETA calculation |
| `--depot NAME` | First stop | Name of the starting / ending stop |

---

## 🌐 Usage — Browser UI

Simply open the HTML file in any modern browser — **no server required**.

```bash
# On Linux / Mac
open route_optimizer_ui.html

# On Windows
start route_optimizer_ui.html
```

### UI Features

| Feature | Description |
|---|---|
| 🗺️ Canvas Map | Real-time route drawn on a coordinate-mapped canvas |
| ➕ Add Stop | Add custom stops by entering name, latitude, longitude |
| ▶️ Optimize Route | Runs Nearest-Neighbor + 2-opt in the browser |
| 📊 Stats Panel | Shows total distance, distance saved %, and estimated time |
| 📋 ETA Table | Per-leg distance and cumulative travel time table |
| 🔄 Reset | Restores default 9 Gwalior stops |
| 🔍 Zoom | Zoom in/out and fit-all controls on the canvas |
| 🚗 Animated Dot | Moving dot shows the travel direction along the route |

---

## 📄 CSV Format

The `stops.csv` file must have exactly three columns:

```csv
name,lat,lon
Home (G-8 Vyankateshwaram),26.2100,78.1870
DB City Mall,26.2164,78.1850
Gwalior Junction Station,26.2162,78.1826
```

| Column | Type | Description |
|---|---|---|
| `name` | string | Display name of the stop |
| `lat` | float | Latitude (decimal degrees) |
| `lon` | float | Longitude (decimal degrees) |

> **Tip:** The first row in the file is used as the depot (start/end point) unless you override it with `--depot`.

---

## 📍 Default Stops — Gwalior City (474011)

| # | Stop Name | Latitude | Longitude |
|---|---|---|---|
| 1 | Home (G-8 Vyankateshwaram) | 26.2100 | 78.1870 |
| 2 | DB City Mall | 26.2164 | 78.1850 |
| 3 | Gwalior Junction Station | 26.2162 | 78.1826 |
| 4 | Gwalior Fort | 26.2218 | 78.1664 |
| 5 | Jai Vilas Palace | 26.2042 | 78.1685 |
| 6 | Jiwaji University | 26.2009 | 78.1987 |
| 7 | Tigra Dam | 26.2176 | 78.0085 |
| 8 | Gwalior Airport | 26.2976 | 78.2260 |
| 9 | Birla Nagar Market | 26.2366 | 78.1939 |

---

## 📊 Sample Output

```
┌──────────────────────────────────────────────┐
│   🗺  Smart Route Optimizer — Gwalior        │
│   City Center, 474011, Madhya Pradesh        │
│   Algorithm: Nearest-Neighbor + 2-opt        │
└──────────────────────────────────────────────┘

  Start / Home:  Home (G-8 Vyankateshwaram)
  Total stops:   9
  Optimizing route... done in 0.012s

  Optimized Route
  ─────────────────────────────────────────────
  🏠  Home (G-8 Vyankateshwaram) ──▶
      DB City Mall ──▶
      Gwalior Junction Station ──▶
      ...
  🏠  Home (G-8 Vyankateshwaram)

  ✓ Optimized distance:  87.43 km
    Naïve distance:       134.21 km
  ✓ Distance saved:      34.9%

  Estimated Travel Times  (avg 30 km/h, city traffic)
  ──────────────────────────────────────────────────────
  Stop                           Leg (km)  Leg time   Cumulative
  ──────────────────────────────────────────────────────
  Home (G-8 Vyankateshwaram)           —         —        0 min
  DB City Mall                      0.76      1 min       1 min
  ...
```

---

## 🔧 Adding Your Own Stops

**Option A — Edit the CSV:**
Open `stops.csv` and add rows in the same `name,lat,lon` format.

**Option B — Use the browser UI:**
Fill in the "Add Stop" form on the left panel and click `+ ADD STOP`.

**Option C — Use interactive mode:**
```bash
python route_optimizer.py --interactive
```

**Finding GPS Coordinates:**
1. Open [Google Maps](https://maps.google.com)
2. Right-click any location → the coordinates appear at the top of the context menu
3. Copy and paste into the CSV or input fields

---

## 📐 Key Functions Reference

### `route_optimizer.py`

| Function | Description |
|---|---|
| `haversine(loc1, loc2)` | Returns great-circle distance in km between two GPS points |
| `build_distance_matrix(locations)` | Builds an n×n distance matrix from a dict of stops |
| `nearest_neighbor(start_idx, dist, n)` | Greedy nearest-neighbor route construction |
| `two_opt(route, dist, time_limit)` | 2-opt local search improvement |
| `optimize(locations, depot)` | Full pipeline — returns optimized route, distance, savings % |
| `eta_table(ordered_names, locations, speed_kmh)` | Prints per-leg and cumulative ETA table |
| `load_csv(filepath)` | Loads stops from a CSV file |
| `interactive_input()` | Prompts user to enter stops manually |

---

## ⚠️ Limitations

- Distances are **straight-line (Haversine)**, not actual road distances. Real road travel may differ.
- 2-opt finds a **locally optimal** solution, not guaranteed globally optimal (NP-hard problem for large n).
- ETA estimates assume **constant average speed** — does not model traffic, signals, or road types.
- For **very large inputs (n > 200)**, runtime may increase significantly.

---

## 🛠️ Possible Extensions

- [ ] Integrate OpenRouteService or OSRM for real road distances
- [ ] Add support for time windows per stop (VRPTW)
- [ ] Export optimized route as GPX file for GPS devices
- [ ] Add or-opt and Lin-Kernighan improvements for larger inputs
- [ ] Django/Flask web server version with live map (Leaflet.js)
- [ ] Mobile-responsive PWA version of the UI

---

## 👩‍💻 Authors

| Name | Enrollment No. | Institute |
|---|---|---|
| Sandhya | BETN1AI23043 | ITM University Gwalior |
| Kartik Patha |  BETN1AI23060 | ITM University Gwalior |
| Mayank Dwivedi |  BETN1AI23044 | ITM University Gwalior |

**Guided by:** Dr. Sanjay Jain, Department of AI & ML, ITM University Gwalior

---

## 📜 License

This project is developed for academic purposes at ITM University Gwalior.
Free to use and modify for educational and non-commercial purposes.

---

*ITM University Gwalior — Jhanshi Road Gwalior – 474001, Madhya Pradesh*
