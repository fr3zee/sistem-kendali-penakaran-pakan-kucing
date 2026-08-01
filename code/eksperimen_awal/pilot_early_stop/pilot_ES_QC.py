#!/usr/bin/env python3
"""
Pilot Early Stop Quality Control Script
Validates parsed data and generates QC report.
"""

import csv
import pandas as pd
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
import numpy as np


# Configuration
INPUT_CSV = Path(r"D:\SKRIPSI\draft\3. dok trial hasil\02_PILOT_EARLY_STOP\pilot_ES_master.csv")
OUTPUT_REPORT = Path(r"D:\SKRIPSI\draft\3. dok trial hasil\02_PILOT_EARLY_STOP\pilot_ES_QC_report.md")


def load_master_csv(csv_path: Path) -> pd.DataFrame:
    """Load the master CSV file."""
    return pd.read_csv(csv_path)


def analyze_trial_distribution(df: pd.DataFrame) -> Dict:
    """
    Analyze trial distribution across Controller × EarlyStop × Setpoint combinations.
    
    Returns:
        Dictionary with distribution analysis
    """
    # Filter only successfully parsed trials
    df_valid_parse = df[df['ParseStatus'] == 'SUCCESS'].copy()
    
    # Group by combination
    grouped = df_valid_parse.groupby(['Controller', 'EarlyStop_g', 'Setpoint_g']).size()
    
    results = {
        'total_parsed': len(df_valid_parse),
        'combinations': {},
        'insufficient': [],
        'extra_trials': [],
        'perfect': []
    }
    
    # Expected combinations: 2 controllers × 3 ES × 4 SP = 24
    controllers = ['Fixed PID', 'Gain Scheduling PID']
    early_stops = [0.2, 0.3, 0.4]
    setpoints = [15.0, 20.0, 25.0, 30.0]
    
    for controller in controllers:
        for es in early_stops:
            for sp in setpoints:
                key = (controller, es, sp)
                count = grouped.get(key, 0)
                
                results['combinations'][key] = count
                
                if count < 3:
                    results['insufficient'].append((key, count))
                elif count > 3:
                    results['extra_trials'].append((key, count))
                else:
                    results['perfect'].append((key, count))
    
    return results


def check_data_completeness(df: pd.DataFrame) -> Dict:
    """
    Check for missing or incomplete data fields.
    
    Returns:
        Dictionary with completeness analysis
    """
    required_fields = [
        'Controller', 'Setpoint_g', 'EarlyStop_g', 'StopTarget_g',
        'FinalMass_g', 'FinalError_g', 'FinalError_pct',
        'Duration_ms', 'Status', 'Valid', 'StopReason'
    ]
    
    issues = []
    
    for idx, row in df.iterrows():
        if row['ParseStatus'] != 'SUCCESS':
            continue
        
        missing = []
        for field in required_fields:
            if pd.isna(row[field]) or row[field] == '':
                missing.append(field)
        
        if missing:
            issues.append({
                'file': row['FileName'],
                'missing_fields': missing
            })
    
    return {
        'total_issues': len(issues),
        'issues': issues
    }


def validate_filename_consistency(df: pd.DataFrame) -> List[Dict]:
    """
    Report files with filename-content mismatches flagged during parsing.
    
    Returns:
        List of files with QC flags
    """
    flagged = []
    
    for idx, row in df.iterrows():
        qc_flags = row['QC_Flags']
        if pd.notna(qc_flags) and str(qc_flags).strip():
            flagged.append({
                'file': row['FileName'],
                'flags': row['QC_Flags']
            })
    
    return flagged


def detect_outliers(df: pd.DataFrame) -> Dict:
    """
    Detect trials with anomalous values.
    
    Returns:
        Dictionary with outlier analysis
    """
    valid_mask = df['Valid'].astype(str).str.upper() == 'TRUE'
    df_valid = df[(df['ParseStatus'] == 'SUCCESS') & valid_mask].copy()
    
    outliers = {
        'error_outliers': [],
        'duration_outliers': [],
        'bridging_outliers': []
    }
    
    # Error outliers: |FinalError_g| > 2× median
    if len(df_valid) > 0:
        median_error = df_valid['FinalError_g'].abs().median()
        threshold_error = 2 * median_error
        
        error_outliers = df_valid[df_valid['FinalError_g'].abs() > threshold_error]
        for idx, row in error_outliers.iterrows():
            outliers['error_outliers'].append({
                'file': row['FileName'],
                'controller': row['Controller'],
                'setpoint': row['Setpoint_g'],
                'early_stop': row['EarlyStop_g'],
                'final_error': row['FinalError_g'],
                'threshold': threshold_error
            })
        
        # Duration outliers: Duration_s > 2× median
        median_duration = df_valid['Duration_s'].median()
        threshold_duration = 2 * median_duration
        
        duration_outliers = df_valid[df_valid['Duration_s'] > threshold_duration]
        for idx, row in duration_outliers.iterrows():
            outliers['duration_outliers'].append({
                'file': row['FileName'],
                'controller': row['Controller'],
                'duration_s': row['Duration_s'],
                'threshold': threshold_duration
            })
        
        # Bridging outliers: BridgingCount > median + 2×SD
        mean_bridging = df_valid['BridgingCount'].mean()
        std_bridging = df_valid['BridgingCount'].std()
        threshold_bridging = mean_bridging + 2 * std_bridging
        
        bridging_outliers = df_valid[df_valid['BridgingCount'] > threshold_bridging]
        for idx, row in bridging_outliers.iterrows():
            outliers['bridging_outliers'].append({
                'file': row['FileName'],
                'controller': row['Controller'],
                'bridging_count': row['BridgingCount'],
                'threshold': threshold_bridging
            })
    
    return outliers


def analyze_validity(df: pd.DataFrame) -> Dict:
    """
    Analyze Valid field and Status distribution.
    
    Returns:
        Dictionary with validity analysis
    """
    df_parsed = df[df['ParseStatus'] == 'SUCCESS'].copy()
    
    valid_counts = df_parsed['Valid'].value_counts().to_dict()
    status_counts = df_parsed['Status'].value_counts().to_dict()
    stop_reason_counts = df_parsed['StopReason'].value_counts().to_dict()
    
    return {
        'valid': valid_counts,
        'status': status_counts,
        'stop_reason': stop_reason_counts
    }


def generate_report(df: pd.DataFrame, output_path: Path):
    """
    Generate comprehensive QC report in Markdown format.
    
    Args:
        df: Master dataframe
        output_path: Path to output report
    """
    # Perform analyses
    distribution = analyze_trial_distribution(df)
    completeness = check_data_completeness(df)
    filename_issues = validate_filename_consistency(df)
    outliers = detect_outliers(df)
    validity = analyze_validity(df)
    
    # Generate report
    report_lines = []
    
    # Header
    report_lines.append("# Pilot Early Stop - Quality Control Report\n")
    report_lines.append(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append("---\n\n")
    
    # Executive Summary
    report_lines.append("## Executive Summary\n\n")
    report_lines.append(f"- **Total files found:** {len(df)}\n")
    report_lines.append(f"- **Successfully parsed:** {distribution['total_parsed']}\n")
    
    valid_mask = df['Valid'].astype(str).str.upper() == 'TRUE'
    df_valid = df[(df['ParseStatus'] == 'SUCCESS') & valid_mask]
    report_lines.append(f"- **Valid trials (Valid=TRUE):** {len(df_valid)}\n")
    
    report_lines.append(f"- **Design minimum (72 trials):** ")
    if len(df) >= 72:
        report_lines.append("✅ **PASS** (found {0} trials)\n".format(len(df)))
    else:
        report_lines.append("❌ **FAIL** (found {0} trials, need 72)\n".format(len(df)))
    
    report_lines.append("\n")
    
    # Trial Distribution Table
    report_lines.append("## Trial Distribution Matrix\n\n")
    report_lines.append("Count of trials per (Controller × Early Stop × Setpoint) combination:\n\n")
    
    # Build distribution table
    controllers = ['Fixed PID', 'Gain Scheduling PID']
    early_stops = [0.2, 0.3, 0.4]
    setpoints = [15.0, 20.0, 25.0, 30.0]
    
    for controller in controllers:
        report_lines.append(f"### {controller}\n\n")
        report_lines.append("| Setpoint | ES 0.2 | ES 0.3 | ES 0.4 |\n")
        report_lines.append("|----------|--------|--------|--------|\n")
        
        for sp in setpoints:
            row = f"| {sp:.0f}g "
            for es in early_stops:
                key = (controller, es, sp)
                count = distribution['combinations'].get(key, 0)
                
                # Mark anomalies
                if count < 3:
                    row += f"| ⚠️ **{count}** "
                elif count > 3:
                    row += f"| ⬆️ **{count}** "
                else:
                    row += f"| ✅ {count} "
            
            row += "|\n"
            report_lines.append(row)
        
        report_lines.append("\n")
    
    # Combination Status
    report_lines.append("## Combination Status\n\n")
    report_lines.append(f"- **Perfect combinations (exactly 3 trials):** {len(distribution['perfect'])}\n")
    report_lines.append(f"- **Insufficient combinations (<3 trials):** {len(distribution['insufficient'])}\n")
    report_lines.append(f"- **Extra trials combinations (>3 trials):** {len(distribution['extra_trials'])}\n\n")
    
    if distribution['insufficient']:
        report_lines.append("### ⚠️ Combinations with <3 Trials\n\n")
        for combo, count in distribution['insufficient']:
            controller, es, sp = combo
            report_lines.append(f"- {controller}, ES={es}g, SP={sp}g: **{count} trial(s)** (need 3)\n")
        report_lines.append("\n")
    
    if distribution['extra_trials']:
        report_lines.append("### ⬆️ Combinations with >3 Trials\n\n")
        for combo, count in distribution['extra_trials']:
            controller, es, sp = combo
            report_lines.append(f"- {controller}, ES={es}g, SP={sp}g: **{count} trials** (extra {count-3})\n")
        report_lines.append("\n")
    
    # Data Quality Issues
    report_lines.append("## Data Quality Issues\n\n")
    
    # Filename mismatches
    if filename_issues:
        report_lines.append(f"### ⚠️ Filename-Content Mismatches ({len(filename_issues)} files)\n\n")
        for issue in filename_issues:
            report_lines.append(f"- **{issue['file']}**: {issue['flags']}\n")
        report_lines.append("\n")
    else:
        report_lines.append("### ✅ Filename-Content Consistency\n\n")
        report_lines.append("All files have consistent filename and content.\n\n")
    
    # Field completeness
    if completeness['total_issues'] > 0:
        report_lines.append(f"### ⚠️ Incomplete Data ({completeness['total_issues']} files)\n\n")
        for issue in completeness['issues'][:10]:  # Show first 10
            report_lines.append(f"- **{issue['file']}**: Missing {', '.join(issue['missing_fields'])}\n")
        if completeness['total_issues'] > 10:
            report_lines.append(f"- ... and {completeness['total_issues'] - 10} more\n")
        report_lines.append("\n")
    else:
        report_lines.append("### ✅ Data Completeness\n\n")
        report_lines.append("All required fields are present in all files.\n\n")
    
    # Validity Summary
    report_lines.append("## Validity Summary\n\n")
    report_lines.append("### Valid Field Distribution\n\n")
    for valid_status, count in validity['valid'].items():
        report_lines.append(f"- **{valid_status}**: {count} trials\n")
    report_lines.append("\n")
    
    report_lines.append("### Status Distribution\n\n")
    for status, count in validity['status'].items():
        report_lines.append(f"- **{status}**: {count} trials\n")
    report_lines.append("\n")
    
    report_lines.append("### Stop Reason Distribution\n\n")
    for reason, count in validity['stop_reason'].items():
        report_lines.append(f"- **{reason}**: {count} trials\n")
    report_lines.append("\n")
    
    # Outliers
    report_lines.append("## Outliers Detected\n\n")
    
    total_outliers = (len(outliers['error_outliers']) + 
                     len(outliers['duration_outliers']) + 
                     len(outliers['bridging_outliers']))
    
    if total_outliers == 0:
        report_lines.append("No significant outliers detected.\n\n")
    else:
        if outliers['error_outliers']:
            report_lines.append(f"### Error Outliers ({len(outliers['error_outliers'])})\n\n")
            for out in outliers['error_outliers']:
                report_lines.append(f"- **{out['file']}**: FinalError={out['final_error']:.2f}g (threshold: {out['threshold']:.2f}g)\n")
            report_lines.append("\n")
        
        if outliers['duration_outliers']:
            report_lines.append(f"### Duration Outliers ({len(outliers['duration_outliers'])})\n\n")
            for out in outliers['duration_outliers']:
                report_lines.append(f"- **{out['file']}**: Duration={out['duration_s']:.1f}s (threshold: {out['threshold']:.1f}s)\n")
            report_lines.append("\n")
        
        if outliers['bridging_outliers']:
            report_lines.append(f"### Bridging Outliers ({len(outliers['bridging_outliers'])})\n\n")
            for out in outliers['bridging_outliers']:
                report_lines.append(f"- **{out['file']}**: Bridging={out['bridging_count']:.0f} (threshold: {out['threshold']:.1f})\n")
            report_lines.append("\n")
    
    # Recommendations
    report_lines.append("## Recommendations\n\n")
    report_lines.append("> [!NOTE]\n")
    report_lines.append("> **Outliers are flagged but NOT removed.** They remain in the master CSV for transparency.\n\n")
    report_lines.append("> [!IMPORTANT]\n")
    report_lines.append("> **Extra trials are preserved.** Two summary datasets will be generated:\n")
    report_lines.append("> 1. All valid trials (uses all data)\n")
    report_lines.append("> 2. Balanced 3-trial (uses first 3 trials per combination for fair comparison)\n\n")
    
    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(report_lines))
    
    print(f"QC report written to: {output_path}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Pilot Early Stop Quality Control")
    print("=" * 60)
    print(f"Input CSV: {INPUT_CSV}")
    print(f"Output Report: {OUTPUT_REPORT}")
    print()
    
    if not INPUT_CSV.exists():
        print(f"ERROR: Input CSV not found: {INPUT_CSV}")
        return
    
    # Load data
    print("Loading master CSV...")
    df = load_master_csv(INPUT_CSV)
    print(f"Loaded {len(df)} rows\n")
    
    # Generate report
    print("Generating QC report...")
    generate_report(df, OUTPUT_REPORT)
    
    print("\n" + "=" * 60)
    print("QC analysis complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
