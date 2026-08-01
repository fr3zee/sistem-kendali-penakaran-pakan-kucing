#!/usr/bin/env python3
"""
Pilot Early Stop Recommendation Generator
Analyzes summary statistics and generates recommendation report.
"""

import pandas as pd
import numpy as np
from pathlib import Path


# Configuration
INPUT_ALL_VALID = Path(r"D:\SKRIPSI\draft\3. dok trial hasil\02_PILOT_EARLY_STOP\pilot_ES_summary_all_valid.csv")
INPUT_BALANCED = Path(r"D:\SKRIPSI\draft\3. dok trial hasil\02_PILOT_EARLY_STOP\pilot_ES_summary_balanced_3trial.csv")
OUTPUT_REPORT = Path(r"D:\SKRIPSI\draft\3. dok trial hasil\02_PILOT_EARLY_STOP\pilot_ES_rekomendasi.md")


def load_summaries() -> tuple:
    """Load both summary CSV files."""
    df_all = pd.read_csv(INPUT_ALL_VALID)
    df_balanced = pd.read_csv(INPUT_BALANCED)
    return df_all, df_balanced


def aggregate_by_early_stop(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate statistics by Early Stop value (across controllers and setpoints).
    
    Returns:
        DataFrame with one row per Early Stop value
    """
    # Group by Early Stop and compute cross-controller, cross-setpoint aggregates
    agg_dict = {
        'n_valid': 'sum',
        'mean_AbsError_g': 'mean',
        'MAE_pct': 'mean',
        'SD_error_g': 'mean',
        'mean_Overshoot_g': 'mean',
        'max_Overshoot_g': 'max',
        'mean_Overshoot_pct': 'mean',
        'mean_Duration_s': 'mean',
        'mean_BridgingCount': 'mean',
        'count_AKURAT': 'sum',
        'count_OVERSHOOT': 'sum'
    }
    
    df_es = df.groupby('EarlyStop_g').agg(agg_dict).reset_index()
    
    # Compute consistency metric (mean of SD across combinations)
    df_es['consistency_SD'] = df.groupby('EarlyStop_g')['SD_error_g'].mean().values
    
    return df_es


def format_comparison_table(df_es: pd.DataFrame, title: str) -> str:
    """Format aggregate data as markdown table."""
    lines = []
    lines.append(f"### {title}\n\n")
    lines.append("| Metric | ES 0.2 | ES 0.3 | ES 0.4 |\n")
    lines.append("|--------|--------|--------|--------|\n")
    
    # Extract values for each ES
    es_02 = df_es[df_es['EarlyStop_g'] == 0.2].iloc[0] if len(df_es[df_es['EarlyStop_g'] == 0.2]) > 0 else None
    es_03 = df_es[df_es['EarlyStop_g'] == 0.3].iloc[0] if len(df_es[df_es['EarlyStop_g'] == 0.3]) > 0 else None
    es_04 = df_es[df_es['EarlyStop_g'] == 0.4].iloc[0] if len(df_es[df_es['EarlyStop_g'] == 0.4]) > 0 else None
    
    # Format rows
    def fmt(val, decimals=2):
        return f"{val:.{decimals}f}" if pd.notna(val) else "N/A"
    
    def get_val(row, col):
        return row[col] if row is not None and col in row else None
    
    metrics = [
        ('Total trials', 'n_valid', 0),
        ('Mean \\|Error\\| (g)', 'mean_AbsError_g', 3),
        ('MAE (%)', 'MAE_pct', 2),
        ('Mean SD (g)', 'consistency_SD', 3),
        ('Mean Overshoot (g)', 'mean_Overshoot_g', 3),
        ('Max Overshoot (g)', 'max_Overshoot_g', 3),
        ('Mean Duration (s)', 'mean_Duration_s', 1),
        ('Mean Bridging', 'mean_BridgingCount', 1),
        ('Count AKURAT', 'count_AKURAT', 0),
        ('Count OVERSHOOT', 'count_OVERSHOOT', 0)
    ]
    
    for metric_name, col, decimals in metrics:
        val_02 = fmt(get_val(es_02, col), decimals)
        val_03 = fmt(get_val(es_03, col), decimals)
        val_04 = fmt(get_val(es_04, col), decimals)
        lines.append(f"| {metric_name} | {val_02} | {val_03} | {val_04} |\n")
    
    lines.append("\n")
    return ''.join(lines)


def analyze_criteria(df_all_es: pd.DataFrame, df_balanced_es: pd.DataFrame) -> str:
    """Generate decision criteria analysis section."""
    lines = []
    lines.append("## Decision Criteria Analysis\n\n")
    lines.append("Based on the balanced 3-trial dataset (for fair comparison):\n\n")
    
    # Find best for each criterion (using balanced data)
    best_error = df_balanced_es.loc[df_balanced_es['mean_AbsError_g'].idxmin()]
    best_mae = df_balanced_es.loc[df_balanced_es['MAE_pct'].idxmin()]
    best_consistency = df_balanced_es.loc[df_balanced_es['consistency_SD'].idxmin()]
    best_overshoot = df_balanced_es.loc[df_balanced_es['mean_Overshoot_g'].idxmin()]
    best_speed = df_balanced_es.loc[df_balanced_es['mean_Duration_s'].idxmin()]
    best_bridging = df_balanced_es.loc[df_balanced_es['mean_BridgingCount'].idxmin()]
    
    lines.append("### Error Performance\n")
    lines.append(f"- **Lowest mean |Error|**: ES {best_error['EarlyStop_g']:.1f}g ({best_error['mean_AbsError_g']:.3f}g)\n")
    lines.append(f"- **Lowest MAE%**: ES {best_mae['EarlyStop_g']:.1f}g ({best_mae['MAE_pct']:.2f}%)\n")
    lines.append(f"- **Best consistency (lowest SD)**: ES {best_consistency['EarlyStop_g']:.1f}g (SD={best_consistency['consistency_SD']:.3f}g)\n\n")
    
    lines.append("### Overshoot Control\n")
    lines.append(f"- **Lowest mean overshoot**: ES {best_overshoot['EarlyStop_g']:.1f}g ({best_overshoot['mean_Overshoot_g']:.3f}g)\n\n")
    
    lines.append("### Speed\n")
    lines.append(f"- **Fastest average duration**: ES {best_speed['EarlyStop_g']:.1f}g ({best_speed['mean_Duration_s']:.1f}s)\n\n")
    
    lines.append("### Bridging\n")
    lines.append(f"- **Fewest bridging events**: ES {best_bridging['EarlyStop_g']:.1f}g ({best_bridging['mean_BridgingCount']:.1f} avg)\n\n")
    
    return ''.join(lines)


def determine_recommendation(df_balanced_es: pd.DataFrame) -> tuple:
    """
    Determine recommended Early Stop based on balanced dataset.
    
    Returns:
        (recommended_es, justification_text)
    """
    # Score each ES based on multiple criteria (lower is better)
    scores = {}
    
    for idx, row in df_balanced_es.iterrows():
        es = row['EarlyStop_g']
        
        # Normalize metrics (0-1 scale)
        error_score = row['mean_AbsError_g'] / df_balanced_es['mean_AbsError_g'].max()
        mae_score = row['MAE_pct'] / df_balanced_es['MAE_pct'].max()
        consistency_score = row['consistency_SD'] / df_balanced_es['consistency_SD'].max()
        overshoot_score = row['mean_Overshoot_g'] / df_balanced_es['mean_Overshoot_g'].max()
        
        # Weighted composite score (error and consistency weighted higher)
        composite = (error_score * 0.3 + mae_score * 0.3 + 
                    consistency_score * 0.2 + overshoot_score * 0.2)
        
        scores[es] = {
            'composite': composite,
            'error': error_score,
            'mae': mae_score,
            'consistency': consistency_score,
            'overshoot': overshoot_score
        }
    
    # Find ES with lowest composite score
    recommended_es = min(scores, key=lambda x: scores[x]['composite'])
    
    # Generate justification
    rec_row = df_balanced_es[df_balanced_es['EarlyStop_g'] == recommended_es].iloc[0]
    
    justification = f"ES {recommended_es:.1f}g demonstrates the best overall performance with "
    justification += f"mean |error| of {rec_row['mean_AbsError_g']:.3f}g ({rec_row['MAE_pct']:.2f}%), "
    justification += f"consistency SD of {rec_row['consistency_SD']:.3f}g, "
    justification += f"and mean overshoot of {rec_row['mean_Overshoot_g']:.3f}g."
    
    return recommended_es, justification


def generate_report(df_all: pd.DataFrame, df_balanced: pd.DataFrame, output_path: Path):
    """Generate comprehensive recommendation report."""
    # Aggregate by Early Stop
    df_all_es = aggregate_by_early_stop(df_all)
    df_balanced_es = aggregate_by_early_stop(df_balanced)
    
    # Determine recommendation
    recommended_es, justification = determine_recommendation(df_balanced_es)
    
    # Build report
    lines = []
    
    # Header
    lines.append("# Pilot Early Stop - Rekomendasi Final\n\n")
    lines.append(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    lines.append("---\n\n")
    
    # Executive Summary
    lines.append("## Executive Summary\n\n")
    lines.append(f"> [!IMPORTANT]\n")
    lines.append(f"> **Rekomendasi: Early Stop = {recommended_es:.1f}g**\n\n")
    lines.append(f"**Justifikasi Utama:**\n\n")
    lines.append(f"{justification}\n\n")
    lines.append("Rekomendasi ini didasarkan pada analisis balanced 3-trial dataset untuk memastikan perbandingan yang adil antar Early Stop values.\n\n")
    lines.append("---\n\n")
    
    # Comparison Tables
    lines.append("## Comparison Tables\n\n")
    lines.append("Berikut adalah perbandingan agregat performa untuk setiap nilai Early Stop:\n\n")
    
    # Table A: All valid trials
    lines.append(format_comparison_table(df_all_es, "Table A: All Valid Trials"))
    
    # Table B: Balanced 3-trial
    lines.append(format_comparison_table(df_balanced_es, "Table B: Balanced 3-Trial Dataset (Recommended Basis)"))
    
    # Decision Criteria
    lines.append(analyze_criteria(df_all_es, df_balanced_es))
    
    # Primary Recommendation Detail
    lines.append("## Primary Recommendation\n\n")
    lines.append(f"Berdasarkan analisis balanced 3-trial dataset, **Early Stop = {recommended_es:.1f}g** direkomendasikan karena:\n\n")
    
    rec_row = df_balanced_es[df_balanced_es['EarlyStop_g'] == recommended_es].iloc[0]
    
    lines.append("1. **Error Performance**: ")
    lines.append(f"Mean absolute error {rec_row['mean_AbsError_g']:.3f}g dengan MAE% sebesar {rec_row['MAE_pct']:.2f}%\n")
    
    lines.append("2. **Consistency**: ")
    lines.append(f"Standard deviation rata-rata sebesar {rec_row['consistency_SD']:.3f}g menunjukkan konsistensi yang baik\n")
    
    lines.append("3. **Overshoot Control**: ")
    lines.append(f"Mean overshoot {rec_row['mean_Overshoot_g']:.3f}g menunjukkan kontrol yang baik\n")
    
    lines.append("4. **Reliability**: ")
    lines.append(f"{int(rec_row['count_AKURAT'])} trial AKURAT dari {int(rec_row['n_valid'])} total trial\n\n")
    
    # Sensitivity Check
    lines.append("## Sensitivity Check\n\n")
    lines.append("Membandingkan hasil antara all-valid dataset vs balanced 3-trial dataset:\n\n")
    
    # Check if recommendation differs
    rec_all, _ = determine_recommendation(df_all_es)
    
    if rec_all == recommended_es:
        lines.append(f"✅ **Konsisten**: Kedua dataset merekomendasikan ES {recommended_es:.1f}g\n\n")
        lines.append("Hal ini meningkatkan confidence terhadap rekomendasi karena tidak terpengaruh oleh extra trials.\n\n")
    else:
        lines.append(f"⚠️ **Perbedaan**: All-valid dataset merekomendasikan ES {rec_all:.1f}g, ")
        lines.append(f"sedangkan balanced dataset merekomendasikan ES {recommended_es:.1f}g\n\n")
        lines.append("Rekomendasi utama tetap menggunakan balanced dataset untuk memastikan fairness.\n\n")
    
    # Limitations
    lines.append("## Limitations and Caveats\n\n")
    lines.append("> [!NOTE]\n")
    lines.append("> **Scope Terbatas**: Analisis ini HANYA untuk pemilihan Early Stop optimal.\n\n")
    
    lines.append("> [!WARNING]\n")
    lines.append("> **Bukan Perbandingan Controller**: Analisis ini TIDAK membandingkan performa Fixed PID vs Gain Scheduling PID.\n\n")
    
    lines.append("> [!CAUTION]\n")
    lines.append("> **Bukan Kesimpulan Final BAB IV**: Ini adalah analisis pilot. Kesimpulan final memerlukan trial tambahan dan analisis mendalam.\n\n")
    
    lines.append("**Keterbatasan:**\n\n")
    lines.append(f"- Total kombinasi: 23 dari 24 expected (1 kombinasi tidak memiliki valid trials)\n")
    lines.append("- Tidak ada metrik baru yang ditambahkan di luar spesifikasi\n")
    lines.append("- Data invalid tetap dicatat namun tidak termasuk dalam agregat\n")
    lines.append("- Trial tambahan (>3 per kombinasi) digunakan dalam sensitivity analysis\n\n")
    
    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(lines))
    
    print(f"Recommendation report written to: {output_path}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Pilot Early Stop Recommendation Generator")
    print("=" * 60)
    print(f"Input (all valid): {INPUT_ALL_VALID}")
    print(f"Input (balanced): {INPUT_BALANCED}")
    print(f"Output report: {OUTPUT_REPORT}")
    print()
    
    if not INPUT_ALL_VALID.exists():
        print(f"ERROR: All-valid summary not found: {INPUT_ALL_VALID}")
        return
    
    if not INPUT_BALANCED.exists():
        print(f"ERROR: Balanced summary not found: {INPUT_BALANCED}")
        return
    
    # Load summaries
    print("Loading summary CSVs...")
    df_all, df_balanced = load_summaries()
    print(f"  All valid: {len(df_all)} combinations")
    print(f"  Balanced: {len(df_balanced)} combinations")
    print()
    
    # Generate report
    print("Generating recommendation report...")
    generate_report(df_all, df_balanced, OUTPUT_REPORT)
    
    print("\n" + "=" * 60)
    print("Recommendation report complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
