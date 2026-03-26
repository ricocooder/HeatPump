"""
Symulator danych dla HeatPump dashboard.
Wstawia realistyczne dane z ostatnich 24h do lokalnej bazy danych.
Uruchom: python3 simulate_data.py
Opcje:
  --clear   Wyczyść stare dane przed wstawieniem nowych
  --hours N Ile godzin wstecz generować (domyślnie 24)
  --live    Tryb live - dodaje nowy punkt co 4 sekundy (Ctrl+C żeby zatrzymać)
"""

import sqlite3
import random
import math
import time
import argparse
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'myDB.db')

# --- Realistyczne zakresy ---
# temp1 = temperatura zewnętrzna (niska, zmienia się wolno)
# temp2 = temperatura kotła (wyższa, reaguje na grzanie)
# temp3 = temperatura podłogówki (pośrednia, powolna)
# volt  = napięcie zasilania (~220-230V)
# cur   = prąd pompy (0-8A, zależy od wydajności)
# efi   = wydajność pompy (0-100%)

def generate_realistic_data(hours=24, interval_seconds=30):
    """Generuje listę (timestamp, wartości) dla wszystkich sensorów."""
    now = datetime.now()
    start = now - timedelta(hours=hours)

    records = {
        'temp1': [],  # zewnętrzna
        'temp2': [],  # kocioł
        'temp3': [],  # podłogówka
        'volt':  [],
        'cur':   [],
        'efi':   [],
    }

    # Stan początkowy
    t_ext    = 5.0    # zewnętrzna
    t_boiler = 38.0   # kocioł
    t_floor  = 32.0   # podłogówka
    volt     = 228.0
    efi      = 60.0
    pump_on  = True

    current_time = start
    step = 0

    while current_time <= now:
        ts = current_time.strftime('%Y-%m-%d %H:%M:%S')
        hour = current_time.hour

        # Symulacja dobowego cyklu temperatury zewnętrznej
        t_ext_target = 3.0 + 8.0 * math.sin((hour - 6) * math.pi / 12)
        t_ext += (t_ext_target - t_ext) * 0.02 + random.uniform(-0.1, 0.1)

        # Kocioł - grzeje gdy temperatura za niska, chłodzi gdy za wysoka
        boiler_set = 42.0
        if t_boiler < boiler_set - 2:
            pump_on = True
            t_boiler += random.uniform(0.3, 0.8)
        elif t_boiler > boiler_set + 2:
            pump_on = False
            t_boiler -= random.uniform(0.1, 0.4)
        else:
            t_boiler += random.uniform(-0.15, 0.15)

        # Podłogówka reaguje wolniej
        floor_set = 35.0
        if t_floor < floor_set - 1:
            t_floor += random.uniform(0.05, 0.2)
        elif t_floor > floor_set + 1:
            t_floor -= random.uniform(0.05, 0.15)
        else:
            t_floor += random.uniform(-0.08, 0.08)

        # Napięcie - małe fluktuacje
        volt += random.uniform(-0.5, 0.5)
        volt = max(218.0, min(238.0, volt))

        # Wydajność i prąd zależą od trybu
        if pump_on:
            efi_target = 65.0 + 20.0 * math.sin(step * 0.05)
            efi += (efi_target - efi) * 0.1 + random.uniform(-1, 1)
            efi = max(10.0, min(100.0, efi))
            current = 2.0 + (efi / 100.0) * 6.0 + random.uniform(-0.2, 0.2)
        else:
            efi -= random.uniform(1.0, 3.0)
            efi = max(0.0, efi)
            current = random.uniform(0.1, 0.5)

        records['temp1'].append((ts, '1', round(t_ext, 2)))
        records['temp2'].append((ts, '1', round(t_boiler, 2)))
        records['temp3'].append((ts, '1', round(t_floor, 2)))
        records['volt'].append((ts,  '1', round(volt, 2)))
        records['cur'].append((ts,   '1', round(current, 2)))
        records['efi'].append((ts,   '1', round(efi, 2)))

        current_time += timedelta(seconds=interval_seconds)
        step += 1

    return records


def insert_records(conn, table, rows):
    conn.executemany(
        f"INSERT INTO {table} (rDatetime, sensorID, temp) VALUES (?, ?, ?)",
        rows
    )


def clear_recent(conn, hours):
    cutoff = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
    for table in ('temp1', 'temp2', 'temp3', 'volt', 'cur', 'efi'):
        conn.execute(f"DELETE FROM {table} WHERE rDatetime >= ?", (cutoff,))
    print(f"  Usunięto dane od {cutoff}")


def run_simulation(hours=24, clear=False, interval=30):
    print(f"Baza danych: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    if clear:
        print(f"Czyszczenie danych z ostatnich {hours}h...")
        clear_recent(conn, hours)
        conn.commit()

    print(f"Generowanie danych za ostatnie {hours}h (co {interval}s)...")
    records = generate_realistic_data(hours=hours, interval_seconds=interval)

    total = 0
    for table, rows in records.items():
        insert_records(conn, table, rows)
        print(f"  {table}: {len(rows)} rekordów")
        total += len(rows)

    conn.commit()
    conn.close()
    print(f"\nGotowe! Wstawiono {total} rekordów łącznie.")
    print(f"Otwórz: http://localhost:5000/history")


def run_live(interval_seconds=4):
    """Dodaje nowy punkt co interval_seconds sekund — symuluje live dane."""
    print(f"Tryb LIVE — dodaję punkt co {interval_seconds}s. Ctrl+C żeby zatrzymać.\n")

    # Stan startowy
    state = {
        't_ext': 5.0, 't_boiler': 38.0, 't_floor': 32.0,
        'volt': 228.0, 'efi': 60.0, 'pump_on': True, 'step': 0
    }

    try:
        while True:
            conn = sqlite3.connect(DB_PATH)
            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            s = state
            hour = datetime.now().hour

            t_ext_target = 3.0 + 8.0 * math.sin((hour - 6) * math.pi / 12)
            s['t_ext'] += (t_ext_target - s['t_ext']) * 0.02 + random.uniform(-0.1, 0.1)

            boiler_set = 42.0
            if s['t_boiler'] < boiler_set - 2:
                s['pump_on'] = True
                s['t_boiler'] += random.uniform(0.3, 0.8)
            elif s['t_boiler'] > boiler_set + 2:
                s['pump_on'] = False
                s['t_boiler'] -= random.uniform(0.1, 0.4)
            else:
                s['t_boiler'] += random.uniform(-0.15, 0.15)

            floor_set = 35.0
            if s['t_floor'] < floor_set - 1:
                s['t_floor'] += random.uniform(0.05, 0.2)
            elif s['t_floor'] > floor_set + 1:
                s['t_floor'] -= random.uniform(0.05, 0.15)
            else:
                s['t_floor'] += random.uniform(-0.08, 0.08)

            s['volt'] += random.uniform(-0.5, 0.5)
            s['volt'] = max(218.0, min(238.0, s['volt']))

            if s['pump_on']:
                efi_target = 65.0 + 20.0 * math.sin(s['step'] * 0.05)
                s['efi'] += (efi_target - s['efi']) * 0.1 + random.uniform(-1, 1)
                s['efi'] = max(10.0, min(100.0, s['efi']))
                current = 2.0 + (s['efi'] / 100.0) * 6.0 + random.uniform(-0.2, 0.2)
            else:
                s['efi'] -= random.uniform(1.0, 3.0)
                s['efi'] = max(0.0, s['efi'])
                current = random.uniform(0.1, 0.5)

            rows = {
                'temp1': (ts, '1', round(s['t_ext'], 2)),
                'temp2': (ts, '1', round(s['t_boiler'], 2)),
                'temp3': (ts, '1', round(s['t_floor'], 2)),
                'volt':  (ts, '1', round(s['volt'], 2)),
                'cur':   (ts, '1', round(current, 2)),
                'efi':   (ts, '1', round(s['efi'], 2)),
            }

            for table, row in rows.items():
                conn.execute(
                    f"INSERT INTO {table} (rDatetime, sensorID, temp) VALUES (?, ?, ?)", row
                )
            conn.commit()
            conn.close()

            s['step'] += 1
            print(f"[{ts}] ext={s['t_ext']:.1f}°C  kocioł={s['t_boiler']:.1f}°C  "
                  f"podł={s['t_floor']:.1f}°C  I={current:.1f}A  efi={s['efi']:.0f}%")
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\nZatrzymano.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Symulator danych HeatPump')
    parser.add_argument('--clear',  action='store_true', help='Wyczyść dane przed wstawieniem')
    parser.add_argument('--hours',  type=int, default=24, help='Ile godzin historii (domyślnie 24)')
    parser.add_argument('--interval', type=int, default=30, help='Co ile sekund próbka (domyślnie 30)')
    parser.add_argument('--live',   action='store_true', help='Tryb live - dodaje dane na bieżąco')
    args = parser.parse_args()

    if args.live:
        run_live(interval_seconds=4)
    else:
        run_simulation(hours=args.hours, clear=args.clear, interval=args.interval)
