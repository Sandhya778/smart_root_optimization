"""
Route Optimizer — Smart delivery/travel route planning using nearest-neighbor
heuristic + 2-opt improvement. No external map APIs needed.

Usage:
    python route_optimizer.py                  # runs built-in Gwalior demo
    python route_optimizer.py --interactive    # enter your own stops
    python route_optimizer.py --file stops.csv # load from CSV
"""

import math
import random
import time
import argparse
import csv
import sys
from itertools import combinations


# ─────────────────────────────────────────────
#  Demo: Gwalior City stops (474011 area)
# ─────────────────────────────────────────────

DEMO_CITIES = {
    "Home (G-8 Vyankateshwaram)": (26.2100, 78.1870),   # City Center, 474011
    "DB City Mall":               (26.2164, 78.1850),
    "Gwalior Junction Station":   (26.2162, 78.1826),
    "Gwalior Fort":               (26.2218, 78.1664),
    "Jai Vilas Palace":           (26.2042, 78.1685),
    "Jiwaji University":          (26.2009, 78.1987),
    "Tigra Dam":                  (26.2176, 78.0085),
    "Gwalior Airport":            (26.2976, 78.2260),
    "Birla Nagar Market":         (26.2366, 78.1939),
}


# ─────────────────────────────────────────────
#  Distance helpers
# ─────────────────────────────────────────────

def haversine(loc1, loc2):
    """Great-circle distance in km between two (lat, lon) points."""
    R = 6371.0
    lat1, lon1 = map(math.radians, loc1)
    lat2, lon2 = map(math.radians, loc2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def build_distance_matrix(locations):
    names = list(locations.keys())
    n = len(names)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine(locations[names[i]], locations[names[j]])
            dist[i][j] = d
            dist[j][i] = d
    return names, dist


def route_distance(route, dist):
    total = sum(dist[route[i]][route[i + 1]] for i in range(len(route) - 1))
    total += dist[route[-1]][route[0]]
    return total


# ─────────────────────────────────────────────
#  Algorithms
# ─────────────────────────────────────────────

def nearest_neighbor(start_idx, dist, n):
    visited = [False] * n
    route = [start_idx]
    visited[start_idx] = True
    for _ in range(n - 1):
        current = route[-1]
        nearest = min(
            (j for j in range(n) if not visited[j]),
            key=lambda j: dist[current][j]
        )
        route.append(nearest)
        visited[nearest] = True
    return route


def two_opt(route, dist, time_limit=5.0):
    best = route[:]
    best_dist = route_distance(best, dist)
    improved = True
    start = time.time()
    while improved and (time.time() - start) < time_limit:
        improved = False
        for i, j in combinations(range(1, len(best)), 2):
            if j - i == 1:
                continue
            new_route = best[:i] + best[i:j][::-1] + best[j:]
            new_dist = route_distance(new_route, dist)
            if new_dist < best_dist - 1e-6:
                best = new_route
                best_dist = new_dist
                improved = True
                break
    return best, best_dist


def optimize(locations, depot=None):
    names, dist = build_distance_matrix(locations)
    n = len(names)
    if n < 2:
        raise ValueError("Need at least 2 stops.")

    start_idx = names.index(depot) if depot and depot in names else 0

    candidates = {start_idx}
    if n > 4:
        candidates |= set(random.sample(range(n), min(n, 5)))

    best_route, best_dist = None, float("inf")
    for s in candidates:
        r = nearest_neighbor(s, dist, n)
        d = route_distance(r, dist)
        if d < best_dist:
            best_route, best_dist = r, d

    optimized_route, optimized_dist = two_opt(best_route, dist)

    naive_route = list(range(n))
    naive_dist = route_distance(naive_route, dist)
    savings = (naive_dist - optimized_dist) / naive_dist * 100

    ordered_names = [names[i] for i in optimized_route]
    return ordered_names, optimized_dist, savings, naive_dist


# ─────────────────────────────────────────────
#  Display
# ─────────────────────────────────────────────

COLORS = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "cyan":   "\033[96m",
    "red":    "\033[91m",
    "grey":   "\033[90m",
    "white":  "\033[97m",
}

def c(color, text):
    return COLORS.get(color, "") + str(text) + COLORS["reset"]


def print_banner():
    print()
    print(c("cyan", "┌──────────────────────────────────────────────┐"))
    print(c("cyan", "│") + c("bold", "   🗺  Smart Route Optimizer — Gwalior        ") + c("cyan", "│"))
    print(c("cyan", "│") + c("grey", "   City Center, 474011, Madhya Pradesh        ") + c("cyan", "│"))
    print(c("cyan", "│") + c("grey", "   Algorithm: Nearest-Neighbor + 2-opt        ") + c("cyan", "│"))
    print(c("cyan", "└──────────────────────────────────────────────┘"))
    print()


def print_route(ordered_names, total_km, savings, naive_km):
    depot = ordered_names[0]
    print(c("bold", "  Optimized Route"))
    print(c("grey", "  " + "─" * 45))

    full_loop = ordered_names + [depot]
    for i in range(len(full_loop) - 1):
        icon = "🏠" if i == 0 else "📍"
        arrow = c("grey", " ──▶  ")
        print(f"  {icon}  {c('white', full_loop[i])}{arrow}", end="")
        if i == len(full_loop) - 2:
            print(c("yellow", full_loop[i + 1]) + "  🏠")
        else:
            print()

    print()
    print(c("grey", "  " + "─" * 45))
    print(f"  {c('green', '✓ Optimized distance:')}  {c('bold', f'{total_km:.2f} km')}")
    print(f"  {c('grey', '  Naïve distance:')}       {naive_km:.2f} km")
    print(f"  {c('green', '✓ Distance saved:')}      {c('bold', c('green', f'{savings:.1f}%'))}")
    print()


def eta_table(ordered_names, locations, speed_kmh=30):
    """ETA table — default 30 km/h for city driving in Gwalior."""
    print(c("bold", "  Estimated Travel Times") + c("grey", f"  (avg {speed_kmh} km/h, city traffic)"))
    print(c("grey", "  " + "─" * 58))
    print(f"  {'Stop':<30} {'Leg (km)':>8}  {'Leg time':>9}  {'Cumulative':>11}")
    print(c("grey", "  " + "─" * 58))

    cumulative_km = 0.0
    prev = ordered_names[0]
    for i, stop in enumerate(ordered_names):
        if i == 0:
            leg_km = 0.0
            leg_str = "—"
            time_str = "—"
        else:
            leg_km = haversine(locations[prev], locations[stop])
            cumulative_km += leg_km
            leg_str = f"{leg_km:>6.2f}"
            mins = int(leg_km / speed_kmh * 60)
            time_str = f"{mins // 60}h {mins % 60:02d}m" if mins >= 60 else f"{mins} min"

        cum_mins = int(cumulative_km / speed_kmh * 60)
        cum_str = f"{cum_mins // 60}h {cum_mins % 60:02d}m" if cum_mins >= 60 else f"{cum_mins} min"

        row = f"  {stop:<30} {leg_str:>8}  {time_str:>9}  {cum_str:>11}"
        print(c("white", row) if i % 2 == 0 else c("grey", row))
        prev = stop

    # Return leg
    ret_km = haversine(locations[ordered_names[-1]], locations[ordered_names[0]])
    cumulative_km += ret_km
    mins = int(ret_km / speed_kmh * 60)
    time_str = f"{mins // 60}h {mins % 60:02d}m" if mins >= 60 else f"{mins} min"
    cum_mins = int(cumulative_km / speed_kmh * 60)
    cum_str = f"{cum_mins // 60}h {cum_mins % 60:02d}m" if cum_mins >= 60 else f"{cum_mins} min"
    ret_row = f"  {'↩ ' + ordered_names[0]:<30} {ret_km:>8.2f}  {time_str:>9}  {cum_str:>11}"
    print(c("yellow", ret_row))
    print(c("grey", "  " + "─" * 58))
    print()


# ─────────────────────────────────────────────
#  Input modes
# ─────────────────────────────────────────────

def load_csv(filepath):
    locations = {}
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations[row["name"].strip()] = (float(row["lat"]), float(row["lon"]))
    return locations


def interactive_input():
    print(c("yellow", "  Enter your stops (name, latitude, longitude)"))
    print(c("grey",   "  Type 'done' when finished. First stop = your home/depot.\n"))
    locations = {}
    while True:
        raw = input(c("cyan", "  Stop name (or 'done'): ")).strip()
        if raw.lower() == "done":
            if len(locations) < 2:
                print(c("red", "  Need at least 2 stops. Keep going!\n"))
                continue
            break
        if not raw:
            continue
        try:
            lat = float(input(c("grey", "    Latitude:  ")))
            lon = float(input(c("grey", "    Longitude: ")))
            locations[raw] = (lat, lon)
            print(c("green", f"  ✓ Added {raw}\n"))
        except ValueError:
            print(c("red", "  Invalid number, try again.\n"))
    return locations


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Smart Route Optimizer — Gwalior City, 474011",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--interactive", action="store_true",
                        help="Manually enter stop names and coordinates")
    parser.add_argument("--file", metavar="CSV",
                        help="Load stops from a CSV file (columns: name, lat, lon)")
    parser.add_argument("--speed", type=float, default=30,
                        help="Average travel speed in km/h (default: 30 for city)")
    parser.add_argument("--depot", metavar="NAME",
                        help="Name of the starting/ending stop")
    args = parser.parse_args()

    print_banner()

    # ── Load stops ──────────────────────────────
    if args.file:
        try:
            locations = load_csv(args.file)
            print(c("green", f"  ✓ Loaded {len(locations)} stops from {args.file}\n"))
        except Exception as e:
            print(c("red", f"  Error reading file: {e}"))
            sys.exit(1)
    elif args.interactive:
        locations = interactive_input()
        print()
    else:
        print(c("grey", "  Demo: Real stops around Gwalior City Center (474011)."))
        print(c("grey", "  Run with --interactive or --file stops.csv for custom stops.\n"))
        locations = DEMO_CITIES

    if len(locations) < 2:
        print(c("red", "  Need at least 2 stops. Exiting."))
        sys.exit(1)

    # ── Optimize ────────────────────────────────
    depot = args.depot or list(locations.keys())[0]
    print(c("grey", f"  Start / Home:  {depot}"))
    print(c("grey", f"  Total stops:   {len(locations)}"))
    print(c("grey", "  Optimizing route..."), end="", flush=True)

    t0 = time.time()
    ordered, total_km, savings, naive_km = optimize(locations, depot=depot)
    elapsed = time.time() - t0

    print(c("green", f" done in {elapsed:.3f}s\n"))

    # ── Results ─────────────────────────────────
    print_route(ordered, total_km, savings, naive_km)
    eta_table(ordered, locations, speed_kmh=args.speed)

    print(c("grey", "  Tip: use --speed 40 for highway roads, or --file stops.csv to load your own stops.\n"))


if __name__ == "__main__":
    main()
