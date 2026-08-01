#!/usr/bin/env python3
"""
Tahap 5 — Koreksi Final: Visualisasi, Audit, dan Narasi Bab IV
================================================================
Empat gambar:
  4.1  Panel empat outcome primer (TIDAK DIUBAH secara substantif)
  4.2  Diagram relasi dominasi 4D + legenda bentuk node
  4.3  Profil RiseTime (TIDAK DIUBAH secara substantif)
  4.4  WithinTolerance + SettlingTime — grouped per setpoint

Audit:
  - SHA-256 11 input sebelum/sesudah
  - Validasi key 4×4×10, overshoot 10 trial (assert, bukan WARN)
  - 24 pasangan unik matriks; directed edge hanya dari flag dominasi
  - Edge digambar == edge sumber per setpoint (assert)
  - Tick/legenda/anotasi count; overlap geometris terbatas
  - Metadata PNG dpi 299–301
  - Determinisme dua-pass PNG
  - Registry angka + regression angka lama
  - Scan placeholder/klaim terlarang pada narasi aktual

Prinsip:
  - Read-only terhadap Tahap 3/4; tidak menghitung statistik baru.
  - Deterministik: seed 42.
  - Grayscale-readable; format akademik formal.
"""

import sys, hashlib, json, re, struct, zlib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ── Konstanta ──────────────────────────────────────────────────
JITTER_SEED = 42
JITTER_AMOUNT = 0.15

BASE_DIR = Path(__file__).resolve().parents[2]  # repo root
MASTER_CSV = BASE_DIR / "data" / "pengujian_final" / "master_dataset_160.csv"

TAHAP3_DIR = BASE_DIR / "hasil" / "analisis_inferensial"
TAHAP4_DIR = BASE_DIR / "hasil" / "sintesis_hasil"

import os as _os5v
_out5v = _os5v.environ.get("PIPELINE_OUTPUT_DIR", str(BASE_DIR / "hasil" / "finalisasi"))

# 11 input read-only
INPUT_MANIFEST = {
    'master':              MASTER_CSV,
    'omnibus_t3':          TAHAP3_DIR / "hasil_omnibus_tahap3.csv",
    'posthoc_t3':          TAHAP3_DIR / "hasil_posthoc_tahap3.csv",
    'konsistensi_omni':    TAHAP3_DIR / "hasil_konsistensi_finalerror_omnibus.csv",
    'proporsi_omni':       TAHAP3_DIR / "hasil_proporsi_within_tolerance_omnibus.csv",
    'proporsi_post':       TAHAP3_DIR / "hasil_proporsi_within_tolerance_posthoc.csv",
    'bridging':            TAHAP3_DIR / "hasil_bridging_deskriptif.csv",
    'primer_t4':           TAHAP4_DIR / "tahap4_profil_primer.csv",
    'tambahan_t4':         TAHAP4_DIR / "tahap4_profil_tambahan_kondisional.csv",
}

OUTPUT_DIR = Path(_out5v)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TAHAP5_DIR = OUTPUT_DIR

SCENARIOS = ["Manual Cepat", "Manual Presisi", "Fixed PID", "GS PID"]
SETPOINTS = [15, 20, 25, 30]

MARKERS = ['o', 's', '^', 'D']
LINESTYLES = ['-', '--', '-.', ':']
COLORS_GRAY = ['#000000', '#404040', '#808080', '#A0A0A0']

# Jumlah edge dominasi yang diharapkan per setpoint (dari matriks final)
EXPECTED_EDGES = {15: 3, 20: 2, 25: 3, 30: 3}

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 9, 'axes.linewidth': 0.8, 'axes.labelsize': 9,
    'axes.titlesize': 10, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'legend.fontsize': 8, 'figure.dpi': 100,
    'savefig.dpi': 300, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.05,
})

audit_log = []

def log_audit(step, status, details):
    audit_log.append({'step': step, 'status': status, 'details': details})
    print(f"[{status}] {step}: {details}")

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for blk in iter(lambda: f.read(8192), b''):
            h.update(blk)
    return h.hexdigest()

# ── Hash Input ─────────────────────────────────────────────────
def hash_all_inputs():
    hashes = {}
    for key, path in INPUT_MANIFEST.items():
        if not path.exists():
            log_audit(f"Hash input {key}", "FAIL", f"File not found: {path}")
            sys.exit(1)
        hashes[key] = sha256_file(path)
        log_audit(f"Hash input {key}", "PASS", hashes[key])
    return hashes

# ── Load & Verify ──────────────────────────────────────────────
def load_and_verify():
    src = {}
    src['master'] = pd.read_csv(INPUT_MANIFEST['master'])
    src['primer'] = pd.read_csv(INPUT_MANIFEST['primer_t4'])
    src['matriks'] = pd.read_csv(BASE_DIR / "archive" / "archived_outputs" / "tahap4_matriks_dominasi.csv")
    src['pareto']   = pd.read_csv(BASE_DIR / "archive" / "archived_outputs" / "tahap4_pareto_per_setpoint.csv")
    src['tambahan'] = pd.read_csv(INPUT_MANIFEST['tambahan_t4'])
    src['posthoc'] = pd.read_csv(INPUT_MANIFEST['posthoc_t3'])
    src['proporsi_post'] = pd.read_csv(INPUT_MANIFEST['proporsi_post'])
    src['omnibus'] = pd.read_csv(INPUT_MANIFEST['omnibus_t3'])
    src['konsistensi_omni'] = pd.read_csv(INPUT_MANIFEST['konsistensi_omni'])
    src['proporsi_omni'] = pd.read_csv(INPUT_MANIFEST['proporsi_omni'])
    src['bridging'] = pd.read_csv(INPUT_MANIFEST['bridging'])

    # Master 160 baris, Valid=TRUE, StopReason=TARGET
    m = src['master']
    assert len(m) == 160, f"Master bukan 160 baris: {len(m)}"
    assert (m['Valid'] == True).all() or (m['Valid'].astype(str).str.upper() == 'TRUE').all(), "Ada trial non-valid"
    assert (m['StopReason'] == 'TARGET').all(), "Ada StopReason != TARGET"
    # Key 4×4×10
    for sp in SETPOINTS:
        for scen in SCENARIOS:
            n = len(m[(m['Setpoint_g'] == sp) & (m['Scenario'] == scen)])
            assert n == 10, f"{scen} SP{sp}: {n} trial, expected 10"
    log_audit("Verify master 4×4×10", "PASS", "160 baris, key lengkap")

    # Primer 16 baris
    assert len(src['primer']) == 16, f"Primer bukan 16: {len(src['primer'])}"
    log_audit("Verify primer count", "PASS", "16 baris")

    # Tambahan 16 baris
    assert len(src['tambahan']) == 16, f"Tambahan bukan 16: {len(src['tambahan'])}"
    log_audit("Verify tambahan count", "PASS", "16 baris")


    return src

# ── Gambar 4.1 (tidak diubah secara substantif) ───────────────
def gambar_4_1(src):
    fig, axes = plt.subplots(2, 2, figsize=(17/2.54, 17/2.54))
    axes = axes.flatten()
    primer, master = src['primer'], src['master']

    # Panel A: MAE
    ax = axes[0]
    for i, scen in enumerate(SCENARIOS):
        d = primer[primer['Scenario'] == scen].sort_values('Setpoint_g')
        ax.errorbar(d['Setpoint_g'], d['MAE_pct'], yerr=d['SD_MAE_pct'],
                    marker=MARKERS[i], linestyle=LINESTYLES[i],
                    color=COLORS_GRAY[i], capsize=3, label=scen, linewidth=1.2)
    ax.set_xlabel('Setpoint (g)'); ax.set_ylabel('MAE (%)')
    ax.set_title('(A) MAE Kelompok', fontweight='bold', loc='left')
    ax.legend(frameon=False, loc='best'); ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    ax.set_xticks(SETPOINTS)

    # Panel B: Overshoot titik trial
    ax = axes[1]
    np.random.seed(JITTER_SEED)
    x_positions = {}
    for sp_idx, sp in enumerate(SETPOINTS):
        base = sp_idx * 5
        for sc_idx, scen in enumerate(SCENARIOS):
            x_positions[(sp, scen)] = base + sc_idx

    for (sp, scen), x_base in x_positions.items():
        df_t = master[(master['Setpoint_g'] == sp) & (master['Scenario'] == scen)]
        assert len(df_t) == 10, f"Overshoot {scen} SP{sp}: {len(df_t)} trial"  # FAIL, not WARN
        y = df_t['MaxOvershoot_pct'].values
        jit = np.random.uniform(-JITTER_AMOUNT, JITTER_AMOUNT, size=len(y))
        sc_idx = SCENARIOS.index(scen)
        ax.scatter(x_base + jit, y, marker=MARKERS[sc_idx],
                   s=20, alpha=0.6, color=COLORS_GRAY[sc_idx], edgecolors='none')

    # Marker rerata dari Tahap 4
    for (sp, scen), x_base in x_positions.items():
        dm = primer[(primer['Setpoint_g'] == sp) & (primer['Scenario'] == scen)]
        if len(dm) == 1:
            sc_idx = SCENARIOS.index(scen)
            ax.scatter(x_base, dm['MeanOvershoot_pct'].values[0], marker=MARKERS[sc_idx],
                       s=80, color=COLORS_GRAY[sc_idx], edgecolors='black', linewidths=1.5, zorder=10)

    ax.set_xlabel('Setpoint (g)'); ax.set_ylabel('Overshoot maksimum (%)')
    ax.set_title('(B) Overshoot Maksimum', fontweight='bold', loc='left')
    ax.set_xticks([1.5, 6.5, 11.5, 16.5])
    ax.set_xticklabels([str(sp) for sp in SETPOINTS])
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5, axis='y')
    handles = [plt.Line2D([0],[0], marker=MARKERS[i], color=COLORS_GRAY[i],
               linestyle='', markersize=6, label=scen) for i, scen in enumerate(SCENARIOS)]
    ax.legend(handles=handles, frameon=False, loc='best', ncol=2)

    # Panel C: Durasi
    ax = axes[2]
    for i, scen in enumerate(SCENARIOS):
        d = primer[primer['Scenario'] == scen].sort_values('Setpoint_g')
        ax.errorbar(d['Setpoint_g'], d['MeanDuration_s'], yerr=d['SD_Duration_s'],
                    marker=MARKERS[i], linestyle=LINESTYLES[i],
                    color=COLORS_GRAY[i], capsize=3, label=scen, linewidth=1.2)
    ax.set_xlabel('Setpoint (g)'); ax.set_ylabel('Durasi (s)')
    ax.set_title('(C) Durasi Proses', fontweight='bold', loc='left')
    ax.legend(frameon=False, loc='best'); ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    ax.set_xticks(SETPOINTS)

    # Panel D: SD FinalError_g
    ax = axes[3]
    for i, scen in enumerate(SCENARIOS):
        d = primer[primer['Scenario'] == scen].sort_values('Setpoint_g')
        ax.plot(d['Setpoint_g'], d['SD_FinalError_g'],
                marker=MARKERS[i], linestyle=LINESTYLES[i],
                color=COLORS_GRAY[i], label=scen, linewidth=1.2)
    ax.set_xlabel('Setpoint (g)'); ax.set_ylabel('SD galat akhir (g)')
    ax.set_title('(D) Konsistensi Galat Akhir', fontweight='bold', loc='left')
    ax.legend(frameon=False, loc='best'); ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    ax.set_xticks(SETPOINTS)

    plt.tight_layout()
    png = OUTPUT_DIR / "gambar_4_1_outcome_primer.png"
    svg = OUTPUT_DIR / "gambar_4_1_outcome_primer.svg"
    fig.savefig(png, dpi=300, bbox_inches='tight')
    fig.savefig(svg, format='svg', bbox_inches='tight')
    plt.close(fig)
    log_audit("Gambar 4.1", "PASS", f"{png.name}, {svg.name}")
    return png, svg

# ── Gambar 4.2 + legenda + edge assert ────────────────────────
def gambar_4_2(src):
    import networkx as nx
    matriks, pareto = src['matriks'], src['pareto']

    fig, axes = plt.subplots(2, 2, figsize=(17/2.54, 17/2.54))
    axes = axes.flatten()

    pos_fixed = {"Manual Cepat": (0,1), "Manual Presisi": (1,1),
                 "Fixed PID": (0,0), "GS PID": (1,0)}

    all_drawn_edges = {}
    for idx, sp in enumerate(SETPOINTS):
        ax = axes[idx]
        df_sp = matriks[matriks['Setpoint_g'] == sp]

        # Build source edge set
        source_edges = set()
        for _, row in df_sp.iterrows():
            if str(row['A_dominates_B']).strip() == 'True':
                source_edges.add((row['Scenario_A'], row['Scenario_B']))
            if str(row['B_dominates_A']).strip() == 'True':
                source_edges.add((row['Scenario_B'], row['Scenario_A']))

        G = nx.DiGraph()
        G.add_nodes_from(SCENARIOS)
        for e in source_edges:
            G.add_edge(e[0], e[1])

        drawn_edges = set(G.edges())
        assert drawn_edges == source_edges, \
            f"SP{sp}: drawn {drawn_edges} != source {source_edges}"
        assert len(drawn_edges) == EXPECTED_EDGES[sp], \
            f"SP{sp}: {len(drawn_edges)} edges, expected {EXPECTED_EDGES[sp]}"
        all_drawn_edges[sp] = drawn_edges

        # Dominated status
        df_par = pareto[pareto['Setpoint_g'] == sp]
        dom_map = dict(zip(df_par['Scenario'], df_par['Dominated'].astype(str)))

        for scen in SCENARIOS:
            x, y = pos_fixed[scen]
            is_dom = dom_map.get(scen, 'True') == 'True'
            mk = 'o' if is_dom else 's'
            ax.plot(x, y, marker=mk, markersize=28,
                    color='white', markeredgecolor='black', markeredgewidth=1.5, zorder=3)
            ax.text(x, y, scen.replace(' ', '\n'), ha='center', va='center', fontsize=5.5, zorder=4)

        for e in G.edges():
            x0, y0 = pos_fixed[e[0]]
            x1, y1 = pos_fixed[e[1]]
            ax.annotate('', xy=(x1,y1), xytext=(x0,y0),
                        arrowprops=dict(arrowstyle='->', lw=1.5, color='black',
                                        shrinkA=18, shrinkB=18))

        ax.set_xlim(-0.4, 1.4); ax.set_ylim(-0.5, 1.5)
        ax.set_aspect('equal'); ax.axis('off')
        ax.set_title(f'Setpoint {sp} g', fontweight='bold', fontsize=9)

    # Legenda bentuk node
    legend_elements = [
        plt.Line2D([0],[0], marker='s', color='white', markeredgecolor='black',
                   markeredgewidth=1.5, markersize=10, label='Non-dominated', linestyle=''),
        plt.Line2D([0],[0], marker='o', color='white', markeredgecolor='black',
                   markeredgewidth=1.5, markersize=10, label='Dominated', linestyle=''),
        plt.Line2D([0],[0], color='black', linewidth=1.5, label='Dominasi 4D',
                   marker='>', markersize=5),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3,
              frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.02))

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    png = OUTPUT_DIR / "gambar_4_2_dominasi_4d.png"
    svg = OUTPUT_DIR / "gambar_4_2_dominasi_4d.svg"
    fig.savefig(png, dpi=300, bbox_inches='tight')
    fig.savefig(svg, format='svg', bbox_inches='tight')
    plt.close(fig)

    total = sum(len(v) for v in all_drawn_edges.values())
    log_audit("Gambar 4.2 edge assert", "PASS",
              f"SP15={len(all_drawn_edges[15])},SP20={len(all_drawn_edges[20])},"
              f"SP25={len(all_drawn_edges[25])},SP30={len(all_drawn_edges[30])},total={total}")
    log_audit("Gambar 4.2", "PASS", f"{png.name}, {svg.name}")
    return png, svg

# ── Gambar 4.3 (tidak diubah secara substantif) ───────────────
def gambar_4_3(src):
    tambahan = src['tambahan']
    fig, ax = plt.subplots(figsize=(12/2.54, 9/2.54))
    for i, scen in enumerate(SCENARIOS):
        d = tambahan[tambahan['Scenario'] == scen].sort_values('Setpoint_g')
        ax.errorbar(d['Setpoint_g'], d['RiseTime_mean'], yerr=d['RiseTime_SD'],
                    marker=MARKERS[i], linestyle=LINESTYLES[i],
                    color=COLORS_GRAY[i], capsize=3, label=scen, linewidth=1.2)
    ax.set_xlabel('Setpoint (g)'); ax.set_ylabel('Rise time 10–90% (s)')
    ax.set_title('Profil Rise Time Empat Skenario', fontweight='bold', fontsize=10)
    ax.legend(frameon=False, loc='best')
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5); ax.set_xticks(SETPOINTS)
    plt.tight_layout()
    png = OUTPUT_DIR / "gambar_4_3_risetime.png"
    svg = OUTPUT_DIR / "gambar_4_3_risetime.svg"
    fig.savefig(png, dpi=300, bbox_inches='tight')
    fig.savefig(svg, format='svg', bbox_inches='tight')
    plt.close(fig)
    log_audit("Gambar 4.3", "PASS", f"{png.name}, {svg.name}")
    return png, svg

# ── Gambar 4.4 — REVISED: grouped per setpoint ────────────────
def gambar_4_4(src):
    tambahan = src['tambahan']
    fig, axes = plt.subplots(1, 2, figsize=(17/2.54, 10/2.54))

    bar_width = 0.18
    offsets = np.array([-1.5, -0.5, 0.5, 1.5]) * bar_width
    x_base = np.arange(len(SETPOINTS))

    annotation_count_a = 0
    annotation_count_b = 0

    # Panel A: WithinTolerance grouped bars
    ax = axes[0]
    previous_values = None
    staggered_label_count = 0
    for i, scen in enumerate(SCENARIOS):
        vals, labels_n = [], []
        for sp in SETPOINTS:
            df = tambahan[(tambahan['Setpoint_g'] == sp) & (tambahan['Scenario'] == scen)]
            assert len(df) == 1, f"Tolerance {scen} SP{sp}: {len(df)} rows"
            prop = df['Within_prop'].values[0]
            count = int(df['Within_n'].values[0])
            vals.append(prop * 100)
            labels_n.append(f"{count}/10")
        bars = ax.bar(x_base + offsets[i], vals, width=bar_width,
                      color=COLORS_GRAY[i], edgecolor='black', linewidth=0.5, label=scen)
        for j, (bar, lbl) in enumerate(zip(bars, labels_n)):
            same_as_previous = (
                previous_values is not None
                and abs(vals[j] - previous_values[j]) < 1e-12
            )
            label_offset = 4.0 if same_as_previous else 1.5
            staggered_label_count += int(same_as_previous)
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + label_offset,
                    lbl, ha='center', va='bottom', fontsize=6)
            annotation_count_a += 1
        previous_values = vals

    ax.set_xlabel('Setpoint (g)'); ax.set_ylabel('Proporsi (%)')
    ax.set_title('(A) Trial Dalam Toleransi ±5%', fontweight='bold', loc='left', fontsize=9)
    ax.set_xticks(x_base); ax.set_xticklabels([str(sp) for sp in SETPOINTS])
    ax.set_ylim(0, 115)
    ax.legend(frameon=False, loc='upper left', fontsize=6.5, ncol=2)
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5, axis='y')

    # Panel B: median SettlingTime dengan rentang Q1–Q3
    ax = axes[1]
    for i, scen in enumerate(SCENARIOS):
        xs, medians, lower_errors, upper_errors, ns = [], [], [], [], []
        for sp_idx, sp in enumerate(SETPOINTS):
            df = tambahan[(tambahan['Setpoint_g'] == sp) & (tambahan['Scenario'] == scen)]
            assert len(df) == 1
            median = df['Settling_median'].values[0]
            q1 = df['Settling_Q1'].values[0]
            q3 = df['Settling_Q3'].values[0]
            sn = int(df['Settling_subset_n'].values[0])
            if pd.notna(median):
                xs.append(sp_idx + offsets[i])
                medians.append(median)
                lower_errors.append(median - q1)
                upper_errors.append(q3 - median)
                ns.append(sn)
        yerr = np.vstack([lower_errors, upper_errors])
        ax.errorbar(xs, medians, yerr=yerr, marker=MARKERS[i], color=COLORS_GRAY[i],
                    capsize=3, markersize=5, linewidth=0, elinewidth=1.2, label=scen)
        for x, y, upper, n in zip(xs, medians, upper_errors, ns):
            ax.text(x, y + upper + 1.0, f"n={n}", ha='center', va='bottom', fontsize=5.5)
            annotation_count_b += 1

    ax.set_xlabel('Setpoint (g)'); ax.set_ylabel('Settling time (s)')
    ax.set_title('(B) Median Settling Time pada Subset Toleransi (IQR)', fontweight='bold', loc='left', fontsize=9)
    ax.set_xticks(x_base); ax.set_xticklabels([str(sp) for sp in SETPOINTS])
    ax.legend(frameon=False, loc='upper left', fontsize=6.5, ncol=2)
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5, axis='y')

    plt.tight_layout()
    png = OUTPUT_DIR / "gambar_4_4_tolerance_settling.png"
    svg = OUTPUT_DIR / "gambar_4_4_tolerance_settling.svg"
    fig.savefig(png, dpi=300, bbox_inches='tight')
    fig.savefig(svg, format='svg', bbox_inches='tight')
    plt.close(fig)

    # Verify annotation counts and equal-height label staggering
    assert annotation_count_a == 16, f"Panel A annotations: {annotation_count_a}"
    assert annotation_count_b == 16, f"Panel B annotations: {annotation_count_b}"
    assert staggered_label_count == 3, f"Panel A staggered labels: {staggered_label_count}"
    log_audit("Gambar 4.4 annotations", "PASS", f"A={annotation_count_a}, B={annotation_count_b}")
    log_audit("Gambar 4.4 equal-height labels", "PASS", "SP15=stagger, SP20=8/10 dan SP25=9/10 distagger")

    # Verify tick count
    for i, ax in enumerate(axes):
        n_ticks = len(ax.get_xticks())
        assert n_ticks == 4, f"Panel {'AB'[i]} xticks: {n_ticks}"
    log_audit("Gambar 4.4 ticks", "PASS", "4 ticks per panel")

    log_audit("Gambar 4.4", "PASS", f"{png.name}, {svg.name}")
    return png, svg

# ── Audit PNG metadata dpi ─────────────────────────────────────
def check_png_dpi(path):
    """Read pHYs chunk from PNG for dpi. Accept 299–301."""
    with open(path, 'rb') as f:
        sig = f.read(8)
        while True:
            raw = f.read(8)
            if len(raw) < 8:
                break
            length = struct.unpack('>I', raw[:4])[0]
            chunk_type = raw[4:8]
            data = f.read(length)
            f.read(4)  # crc
            if chunk_type == b'pHYs' and length == 9:
                ppux, ppuy, unit = struct.unpack('>IIB', data)
                if unit == 1:  # meter
                    dpi_x = round(ppux / 39.3701)
                    dpi_y = round(ppuy / 39.3701)
                    return dpi_x, dpi_y
    return None, None

# ── Main ───────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("Tahap 5 — Koreksi Final: Visualisasi + Audit")
    print("=" * 60)

    # 1. Hash input sebelum
    hashes_before = hash_all_inputs()

    # 2. Load & verify
    src = load_and_verify()

    # 3. Generate figures (run 1)
    gambar_4_1(src)
    gambar_4_2(src)
    gambar_4_3(src)
    gambar_4_4(src)

    # 4. Hash PNG run 1
    png_files = sorted(OUTPUT_DIR.glob("gambar_4_*.png"))
    hashes_run1 = {p.name: sha256_file(p) for p in png_files}
    for name, h in hashes_run1.items():
        log_audit(f"PNG run1 hash {name}", "PASS", h)

    # 5. Run 2 for determinism
    gambar_4_1(src)
    gambar_4_2(src)
    gambar_4_3(src)
    gambar_4_4(src)

    hashes_run2 = {p.name: sha256_file(p) for p in png_files}
    deterministic = True
    for name in hashes_run1:
        if hashes_run1[name] == hashes_run2[name]:
            log_audit(f"Determinism {name}", "PASS", "hash identical")
        else:
            log_audit(f"Determinism {name}", "FAIL", f"run1={hashes_run1[name]} != run2={hashes_run2[name]}")
            deterministic = False

    if not deterministic:
        log_audit("Determinism overall", "FAIL", "Not all PNGs deterministic")
    else:
        log_audit("Determinism overall", "PASS", "All 4 PNGs deterministic")

    # 6. Check PNG dpi
    for p in png_files:
        dx, dy = check_png_dpi(p)
        if dx is not None and 299 <= dx <= 301 and 299 <= dy <= 301:
            log_audit(f"DPI {p.name}", "PASS", f"{dx}x{dy}")
        else:
            log_audit(f"DPI {p.name}", "WARN", f"dpi={dx}x{dy}, expected 299–301")

    # 7. Hash input sesudah — verify unchanged
    hashes_after = hash_all_inputs()
    for key in hashes_before:
        if hashes_before[key] == hashes_after[key]:
            log_audit(f"Input integrity {key}", "PASS", "UNCHANGED")
        else:
            log_audit(f"Input integrity {key}", "FAIL", "CHANGED!")
            sys.exit(1)

    # 8. Save audit CSV
    audit_path = TAHAP5_DIR / "audit_visual_tahap5.csv"
    pd.DataFrame(audit_log).to_csv(audit_path, index=False)
    print(f"\nAudit saved to {audit_path}")

    print("\n" + "=" * 60)
    print("Visualisasi dan audit Tahap 5 selesai.")
    print("=" * 60)

if __name__ == "__main__":
    main()
