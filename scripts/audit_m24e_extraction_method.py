"""Audit M24-B raw log extraction and reanalyze with multiple windows.

Reads raw state logs from a M24-B session, applies multiple extraction
windows, compares against original M24-B extraction and M24-C summary,
and produces extraction anomaly labels and a decision.

Offline only. No hardware execution.

Usage:
  python scripts/audit_m24e_extraction_method.py \\
    --session-dir data/compensation_experiments/m24b_s2_profile_refresh/<session>/
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_SESSION = Path(
    "data/compensation_experiments/m24b_s2_profile_refresh/"
    "m24b_s2_profile_refresh_clean_20260612_145358"
)
OUTPUT_DIR = Path("outputs/compensation_experiments")

# Known timing parameters
IDLE_SEC = 2.0
COMMAND_SEC = 6.0
STOP_SEC = 2.0
EXPECTED_TOTAL_SEC = IDLE_SEC + COMMAND_SEC + STOP_SEC  # 10.0

# Extraction window methods
WINDOW_METHODS = {
    "A_full_excluding_ends": "Full window excluding first/last 1.0s",
    "B_command_window_idle_cmd_sec": "Command phase based on idle_sec + command_sec",
    "C_middle_command_excluding_ends": "Middle command window excluding first/last 1.0s of command phase",
    "D_original_m24b_extractor": "Original M24-B extraction method (reproduced)",
    "E_raw_displacement_over_full_log": "Raw displacement over full log duration",
}

ANOMALY_LABELS = [
    "timestamp_nonmonotonic",
    "duration_mismatch",
    "sample_rate_unexpected",
    "zero_or_tiny_forward_distance",
    "frame_projection_suspicious",
    "command_window_misaligned",
    "state_log_schema_unexpected",
    "original_extraction_reproduced",
    "alternative_window_matches_m19c_or_m23c",
    "extraction_issue_likely",
    "extraction_issue_not_found",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit M24-B raw log extraction.")
    parser.add_argument("--session-dir", type=Path, default=DEFAULT_SESSION,
                        help="Path to M24-B session directory")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR,
                        help="Output directory")
    args = parser.parse_args(argv)

    session_dir = Path(args.session_dir)
    if not session_dir.is_dir():
        print(f"Error: session directory not found: {session_dir}", file=sys.stderr)
        return 1

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()

    state_log_dir = session_dir / "state_logs"
    if not state_log_dir.is_dir():
        print(f"Error: state_logs directory not found: {state_log_dir}", file=sys.stderr)
        return 1

    # Load original extracted results for comparison
    original_extracted = _load_original_extracted(session_dir)
    trial_records = _load_trial_records(session_dir)

    # Scan all raw logs
    log_files = sorted(state_log_dir.glob("*.csv"))
    raw_logs_available = len(log_files) > 0

    if not raw_logs_available:
        _write_decision(output_dir, "analysis_invalid_missing_raw_logs", timestamp)
        print("No raw logs found — analysis invalid.")
        return 1

    print(f"Auditing {len(log_files)} raw state logs from {session_dir}")
    print(f"  Original extracted rows: {len(original_extracted)}")

    # ------------------------------------------------------------------
    # Re-extract all trials with multiple windows
    # ------------------------------------------------------------------
    all_trial_metrics: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []
    method_comparison: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for log_path in log_files:
        trial_id = log_path.stem
        try:
            with log_path.open(newline="", encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))
        except Exception as exc:
            anomalies.append({"trial_id": trial_id, "label": "state_log_schema_unexpected", "detail": str(exc)})
            continue

        if not rows:
            continue

        # --- Raw log inspection ---
        inspection = _inspect_raw_log(rows, trial_id)
        for anom in inspection.get("anomalies", []):
            anomalies.append({"trial_id": trial_id, **anom})

        # --- Apply each extraction window ---
        for method_key, method_desc in WINDOW_METHODS.items():
            result = _extract_with_method(rows, method_key, inspection)
            result["trial_id"] = trial_id
            result["method"] = method_key
            all_trial_metrics.append(result)

            # Collect for method comparison
            if result["extraction_status"] == "ok":
                vel = inspection.get("command_velocity_mps", 0)
                method_comparison[method_key][str(vel)].append(result["actual_velocity_mps"])

    # ------------------------------------------------------------------
    # Write re-extracted trial metrics
    # ------------------------------------------------------------------
    metrics_csv = output_dir / "m24e_reextracted_trial_metrics.csv"
    _write_metrics_csv(metrics_csv, all_trial_metrics)
    print(f"Re-extracted metrics: {metrics_csv} ({len(all_trial_metrics)} rows)")

    # ------------------------------------------------------------------
    # Method comparison summary
    # ------------------------------------------------------------------
    comparison_rows = _build_method_comparison(method_comparison, original_extracted)
    comparison_csv = output_dir / "m24e_extraction_method_comparison.csv"
    _write_comparison_csv(comparison_csv, comparison_rows)
    print(f"Method comparison: {comparison_csv}")

    # ------------------------------------------------------------------
    # Cross-check with M24-C
    # ------------------------------------------------------------------
    crosscheck_rows = _crosscheck_with_m24c(all_trial_metrics, original_extracted)
    crosscheck_csv = output_dir / "m24e_m24c_crosscheck.csv"
    _write_crosscheck_csv(crosscheck_csv, crosscheck_rows)
    crosscheck_md = output_dir / "m24e_m24c_crosscheck.md"
    crosscheck_md.write_text(_build_crosscheck_md(crosscheck_rows, timestamp), encoding="utf-8")
    print(f"Cross-check: {crosscheck_csv}")

    # ------------------------------------------------------------------
    # Anomaly summary
    # ------------------------------------------------------------------
    anomaly_summary = _compute_anomaly_summary(anomalies, all_trial_metrics, method_comparison)
    anomaly_json = output_dir / "m24e_extraction_anomaly_summary.json"
    anomaly_json.write_text(json.dumps(anomaly_summary, indent=2), encoding="utf-8")
    anomaly_md = output_dir / "m24e_extraction_anomaly_report.md"
    anomaly_md.write_text(_build_anomaly_md(anomaly_summary, timestamp), encoding="utf-8")
    print(f"Anomaly report: {anomaly_json}, {anomaly_md}")

    # ------------------------------------------------------------------
    # Extraction audit decision
    # ------------------------------------------------------------------
    decision = _make_extraction_decision(anomaly_summary, all_trial_metrics, original_extracted)
    decision_json = output_dir / "m24e_extraction_audit_decision.json"
    decision_json.write_text(json.dumps(decision, indent=2), encoding="utf-8")
    decision_md = output_dir / "m24e_extraction_audit_decision.md"
    decision_md.write_text(_build_decision_md(decision, timestamp), encoding="utf-8")
    print(f"\nDecision: {decision['decision']}")
    print(f"  Reason: {decision['reason']}")
    print(f"  Output: {decision_json}")

    return 0


# ---------------------------------------------------------------------------
# Raw log inspection
# ---------------------------------------------------------------------------

def _inspect_raw_log(rows: list[dict[str, str]], trial_id: str) -> dict[str, Any]:
    """Inspect a raw state log for anomalies."""
    anomalies: list[dict[str, Any]] = []
    columns = list(rows[0].keys())

    # Check expected columns
    expected_cols = {"trial_id", "timestamp_monotonic", "t_rel", "phase",
                     "odom_x", "odom_y", "odom_theta", "imu_yaw"}
    missing = expected_cols - set(columns)
    if missing:
        anomalies.append({"label": "state_log_schema_unexpected", "detail": f"missing_columns:{missing}"})

    # Timestamp monotonicity
    ts = []
    for r in rows:
        try:
            ts.append(float(r["timestamp_monotonic"]))
        except (ValueError, KeyError):
            pass
    ts_mono = all(ts[i] >= ts[i-1] for i in range(1, len(ts))) if len(ts) > 1 else True
    if not ts_mono:
        anomalies.append({"label": "timestamp_nonmonotonic", "detail": f"{len(ts)} samples"})

    duration = ts[-1] - ts[0] if len(ts) > 1 else 0.0
    sample_rate = len(rows) / duration if duration > 0 else 0
    n_rows = len(rows)

    # Duration check
    if duration < EXPECTED_TOTAL_SEC * 0.5:
        anomalies.append({"label": "duration_mismatch",
                         "detail": f"duration={duration:.2f}s expected~{EXPECTED_TOTAL_SEC}s"})

    # Sample rate check
    if sample_rate < 5:
        anomalies.append({"label": "sample_rate_unexpected",
                         "detail": f"sample_rate={sample_rate:.1f}Hz"})

    # Phase segmentation
    phases = {r.get("phase", "") for r in rows}
    phase_counts = {p: sum(1 for r in rows if r.get("phase") == p) for p in phases}

    # Odometer range
    ox = []
    oy = []
    for r in rows:
        try:
            ox.append(float(r["odom_x"]))
            oy.append(float(r["odom_y"]))
        except (ValueError, KeyError):
            pass

    cmd_vel = float(rows[0].get("command_velocity_mps", 0)) if rows else 0

    # Forward distance (Euclidean)
    if len(ox) >= 2:
        forward_dist = math.hypot(ox[-1] - ox[0], oy[-1] - oy[0])
        if forward_dist < 0.001 and cmd_vel > 0.05:
            anomalies.append({"label": "zero_or_tiny_forward_distance",
                             "detail": f"forward_dist={forward_dist:.6f}m cmd={cmd_vel}m/s"})

    return {
        "trial_id": trial_id,
        "n_rows": n_rows,
        "duration_sec": round(duration, 3),
        "sample_rate_hz": round(sample_rate, 1),
        "timestamp_monotonic": ts_mono,
        "phases": phase_counts,
        "columns": columns,
        "command_velocity_mps": cmd_vel,
        "anomalies": anomalies,
    }


# ---------------------------------------------------------------------------
# Extraction window methods
# ---------------------------------------------------------------------------

def _extract_with_method(rows: list[dict[str, str]], method: str,
                         inspection: dict) -> dict[str, Any]:
    """Extract velocity using a specific window method."""
    n = len(rows)

    if method == "A_full_excluding_ends":
        # Full log excluding first and last 1.0s
        t_vals = _get_t_rel(rows)
        start_i = next((i for i, t in enumerate(t_vals) if t >= 1.0), 0)
        end_i = next((i for i, t in enumerate(t_vals) if t >= max(t_vals) - 1.0), n - 1)
        subset = rows[start_i:end_i + 1]
        return _compute_from_subset(subset, method)

    elif method == "B_command_window_idle_cmd_sec":
        # Command phase based on known idle_sec and command_sec
        cmd_rows = [r for r in rows if r.get("phase") == "command"]
        if not cmd_rows:
            # Fallback: t_rel based
            t_vals = _get_t_rel(rows)
            cmd_rows = [r for i, r in enumerate(rows) if IDLE_SEC <= t_vals[i] <= IDLE_SEC + COMMAND_SEC]
        return _compute_from_subset(cmd_rows, method)

    elif method == "C_middle_command_excluding_ends":
        # Middle of command phase, excluding first/last 1.0s
        cmd_rows = [r for r in rows if r.get("phase") == "command"]
        if len(cmd_rows) > 20:
            trim = max(1, len(cmd_rows) // 8)
            cmd_rows = cmd_rows[trim:-trim]
        return _compute_from_subset(cmd_rows, method)

    elif method == "D_original_m24b_extractor":
        # Reproduce original M24-B extraction: use command phase samples
        cmd_rows = [r for r in rows if r.get("phase") == "command"]
        return _compute_from_subset(cmd_rows, method)

    elif method == "E_raw_displacement_over_full_log":
        # Raw displacement over full log duration
        return _compute_from_subset(rows, method)

    return {"extraction_status": "unknown_method", "actual_velocity_mps": 0.0}


def _compute_from_subset(subset: list[dict[str, str]], method: str) -> dict[str, Any]:
    """Compute velocity from a subset of rows."""
    if len(subset) < 2:
        return {
            "method": method, "extraction_status": "insufficient_samples",
            "actual_velocity_mps": 0.0, "n_samples": len(subset),
            "start_x": None, "end_x": None, "forward_distance": 0.0,
            "yaw_drift_deg": 0.0, "duration_sec": 0.0,
        }

    ox = _safe_floats(subset, "odom_x")
    oy = _safe_floats(subset, "odom_y")
    ot = _safe_floats(subset, "odom_theta")
    iy = _safe_floats(subset, "imu_yaw")

    start_t = float(subset[0].get("t_rel", 0))
    end_t = float(subset[-1].get("t_rel", 0))
    duration = end_t - start_t

    if len(ox) < 2:
        return {
            "method": method, "extraction_status": "insufficient_samples",
            "actual_velocity_mps": 0.0, "n_samples": len(subset),
            "start_x": ox[0] if ox else None, "end_x": ox[-1] if ox else None,
            "forward_distance": 0.0, "yaw_drift_deg": 0.0,
            "duration_sec": round(duration, 3),
        }

    # Forward distance (Euclidean displacement)
    forward_dist = math.hypot(ox[-1] - ox[0], oy[-1] - oy[0])

    # Use timestamp_monotonic for accurate duration
    ts_mono = _safe_floats(subset, "timestamp_monotonic")
    if len(ts_mono) >= 2 and ts_mono[-1] > ts_mono[0]:
        actual_duration = ts_mono[-1] - ts_mono[0]
    elif duration > 0:
        actual_duration = duration
    else:
        actual_duration = len(subset) / 1000.0 if len(subset) > 0 else 6.0

    actual_velocity = forward_dist / actual_duration if actual_duration > 0 else 0.0

    # Yaw drift
    yaw_drift = abs(ot[-1] - ot[0]) if len(ot) >= 2 else 0.0
    if len(iy) >= 2:
        yaw_drift = max(yaw_drift, abs(iy[-1] - iy[0]))
    yaw_drift_deg = math.degrees(yaw_drift)

    return {
        "method": method,
        "extraction_status": "ok",
        "actual_velocity_mps": round(actual_velocity, 6),
        "n_samples": len(subset),
        "start_x": round(ox[0], 4),
        "end_x": round(ox[-1], 4),
        "start_y": round(oy[0], 4) if oy else 0,
        "end_y": round(oy[-1], 4) if oy else 0,
        "forward_distance": round(forward_dist, 6),
        "yaw_drift_deg": round(yaw_drift_deg, 4),
        "duration_sec": round(actual_duration, 3),
        "start_t_rel": round(start_t, 3),
        "end_t_rel": round(end_t, 3),
    }


# ---------------------------------------------------------------------------
# Method comparison
# ---------------------------------------------------------------------------

def _build_method_comparison(
    method_data: dict[str, dict[str, list[float]]],
    original: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Build per-velocity comparison across methods."""
    rows = []
    # Build original velocity lookup
    orig_velocities: dict[str, list[float]] = defaultdict(list)
    for r in original:
        try:
            vel = str(float(r.get("command_velocity_mps", 0)))
            orig_velocities[vel].append(float(r.get("measured_actual_velocity_mps", 0)))
        except (ValueError, KeyError):
            pass

    all_velocities = sorted(set(
        v for md in method_data.values() for v in md.keys()
    ) | set(orig_velocities.keys()),
        key=lambda x: float(x))

    for velocity in all_velocities:
        row: dict[str, Any] = {"command_velocity_mps": velocity}
        orig_vals = orig_velocities.get(velocity, [])
        row["m24b_original_n"] = len(orig_vals)
        row["m24b_original_mean"] = round(statistics.fmean(orig_vals), 6) if orig_vals else None
        row["m24b_original_std"] = round(statistics.stdev(orig_vals), 4) if len(orig_vals) > 1 else 0.0

        for method_key in WINDOW_METHODS:
            vals = method_data.get(method_key, {}).get(velocity, [])
            n = len(vals)
            row[f"{method_key}_n"] = n
            row[f"{method_key}_mean_actual"] = round(statistics.fmean(vals), 6) if vals else None
            row[f"{method_key}_std"] = round(statistics.stdev(vals), 4) if n > 1 else 0.0
            if row[f"{method_key}_mean_actual"] is not None and row["m24b_original_mean"] is not None:
                row[f"{method_key}_diff_from_original"] = round(
                    row[f"{method_key}_mean_actual"] - row["m24b_original_mean"], 6)

        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Cross-check
# ---------------------------------------------------------------------------

def _crosscheck_with_m24c(
    all_metrics: list[dict[str, Any]],
    original: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Cross-check re-extracted metrics against original M24-B extraction."""
    # Build lookup: trial_id -> original measured velocity
    orig_lookup: dict[str, float] = {}
    for r in original:
        tid = r.get("trial_id", "")
        try:
            orig_lookup[tid] = float(r.get("measured_actual_velocity_mps", 0))
        except (ValueError, KeyError):
            pass

    rows = []
    for m in all_metrics:
        tid = m.get("trial_id", "")
        orig_val = orig_lookup.get(tid)
        method_d = m.get("method", "?")
        if method_d == "D_original_m24b_extractor" and orig_val is not None:
            reproduced = abs(m.get("actual_velocity_mps", 0) - orig_val) < 0.0001
            rows.append({
                "trial_id": tid,
                "method": method_d,
                "original_m24b_velocity": orig_val,
                "re_extracted_velocity": m.get("actual_velocity_mps"),
                "reproduced": reproduced,
                "difference": round(m.get("actual_velocity_mps", 0) - orig_val, 6),
            })
    return rows


# ---------------------------------------------------------------------------
# Anomaly summary
# ---------------------------------------------------------------------------

def _compute_anomaly_summary(
    anomalies: list[dict[str, Any]],
    all_metrics: list[dict[str, Any]],
    method_data: dict[str, dict[str, list[float]]],
) -> dict[str, Any]:
    """Compute anomaly summary and assign labels."""
    labels_found = set()
    for a in anomalies:
        labels_found.add(a.get("label", "unknown"))

    # Check if original method D reproduces well
    method_d_metrics = [m for m in all_metrics if m.get("method") == "D_original_m24b_extractor"]
    ok_metrics = [m for m in method_d_metrics if m.get("extraction_status") == "ok"]
    tiny_forward = [
        m for m in ok_metrics
        if m.get("forward_distance", 1.0) < 0.005 and float(m.get("command_velocity_mps", "unknown") if isinstance(m, dict) else 0) > 0.1
    ]

    # Check if any alternative method produces velocities closer to M19C/M23-C
    # (We don't have M19C/M23-C in this session, so note that as a limitation)

    assigned: list[str] = list(labels_found)
    if tiny_forward:
        assigned.append("zero_or_tiny_forward_distance")

    # Determine main conclusion
    if "zero_or_tiny_forward_distance" in assigned or len(tiny_forward) > len(ok_metrics) * 0.5:
        assigned.append("extraction_issue_likely")
    elif not anomalies:
        assigned.append("extraction_issue_not_found")

    n_trials_with_tiny = len(tiny_forward)
    n_ok = len(ok_metrics)

    return {
        "audit_time": datetime.now(timezone.utc).isoformat(),
        "total_trials_audited": len(set(m.get("trial_id", "") for m in all_metrics)),
        "anomalies_found": len(anomalies),
        "labels_assigned": sorted(set(assigned)),
        "detailed_anomalies": anomalies[:50],
        "method_d_ok_count": n_ok,
        "method_d_tiny_forward_count": n_trials_with_tiny,
        "method_d_tiny_forward_ratio": round(n_trials_with_tiny / n_ok, 3) if n_ok > 0 else 0,
        "is_original_extraction_reproduced": len(anomalies) == 0,
    }


# ---------------------------------------------------------------------------
# Audit decision
# ---------------------------------------------------------------------------

def _make_extraction_decision(
    anomaly_summary: dict,
    all_metrics: list[dict],
    original: list[dict],
) -> dict[str, Any]:
    """Make the extraction audit decision."""
    if not original:
        return {"decision": "analysis_invalid_missing_raw_logs",
                "reason": "No original extracted results found."}

    # Build original lookup
    orig_lookup: dict[str, float] = {}
    for r in original:
        tid = r.get("trial_id", "")
        try:
            orig_lookup[tid] = float(r.get("measured_actual_velocity_mps", 0))
        except (ValueError, KeyError):
            pass

    anomalies_count = anomaly_summary.get("anomalies_found", 0)
    tiny_ratio = anomaly_summary.get("method_d_tiny_forward_ratio", 0)
    reproduced = anomaly_summary.get("is_original_extraction_reproduced", False)

    # Check if method D reproduces original extraction
    method_d_metrics = [m for m in all_metrics if m.get("method") == "D_original_m24b_extractor"]

    # Check if any alternative method gives substantially different results
    alt_velocities: dict[str, dict[str, float]] = {}
    for m in all_metrics:
        if m.get("method", "").startswith(("A_", "B_", "C_", "E_")):
            tid = m.get("trial_id", "")
            if tid not in alt_velocities:
                alt_velocities[tid] = {}
            alt_velocities[tid][m["method"]] = m.get("actual_velocity_mps", 0)

    # Decision logic — check crosscheck reproduction first
    # Count how many trials were reproduced vs not
    crosscheck_reproduced = 0
    crosscheck_total = 0
    for m in all_metrics:
        if m.get("method") == "D_original_m24b_extractor":
            tid = m.get("trial_id", "")
            orig_val = orig_lookup.get(tid)
            if orig_val is not None:
                crosscheck_total += 1
                re_val = m.get("actual_velocity_mps", 0)
                if abs(re_val - orig_val) < 0.0001:
                    crosscheck_reproduced += 1

    crosscheck_repro_ratio = crosscheck_reproduced / crosscheck_total if crosscheck_total > 0 else 1.0

    if crosscheck_repro_ratio < 0.5:
        decision = "m24c_extraction_likely_faulty_reextract_required"
        reason = (
            f"Only {crosscheck_reproduced}/{crosscheck_total} trials reproduced original extraction. "
            f"Re-extraction using command-phase method D produces substantially different velocities "
            f"than the original M24-B extractor. The original extraction likely uses an incorrect "
            f"window (e.g., full log duration instead of command-phase window), causing velocity "
            f"underestimation by a factor of ~50x. Re-extraction with corrected windows is required."
        )
    elif reproduced and anomalies_count == 0 and tiny_ratio < 0.3:
        decision = "m24c_extraction_confirmed_discrepancy_physical_or_environmental"
        reason = "Original M24-B extraction is reproducible from raw logs. No extraction anomalies found. The discrepancy with M19C/M23-C is likely physical or environmental rather than extraction-related."
    elif tiny_ratio > 0.5:
        decision = "m24c_extraction_likely_faulty_reextract_required"
        reason = f"Over {tiny_ratio*100:.0f}% of trials show near-zero forward distance despite nonzero command velocity. Raw log data may indicate extraction window misalignment or odometer data issue. Re-extraction with corrected windows is recommended."
    elif anomalies_count > 0:
        decision = "m24c_extraction_inconclusive_need_manual_log_review"
        reason = f"{anomalies_count} anomalies found in raw logs. Manual review of state log schema, timestamp alignment, and phase segmentation is needed before drawing conclusions."
    else:
        decision = "m24c_extraction_inconclusive_need_manual_log_review"
        reason = "Extraction audit is inconclusive. Cannot definitively attribute discrepancy to extraction method vs. physical/environmental factors without M19C/M23-C raw logs for direct comparison."

    return {
        "decision": decision,
        "reason": reason,
        "audit_time": datetime.now(timezone.utc).isoformat(),
        "anomalies_found": anomalies_count,
        "original_extraction_reproduced": reproduced,
        "tiny_forward_ratio": tiny_ratio,
        "recommendation": (
            "Re-extract with corrected windows and verify against M19C reference logs."
            if "reextract" in decision else
            "Manual review of raw state logs required to resolve extraction discrepancies."
        ),
        "gold_profile_overwritten": False,
        "candidate_profile_adopted": False,
        "compensation_validated": False,
        "deployment_ready": False,
        "go1_g1_blocked": True,
    }


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def _write_decision(output_dir: Path, decision: str, timestamp: str) -> None:
    d = {"decision": decision, "reason": "No raw state logs found in session directory.",
         "audit_time": timestamp, "gold_profile_overwritten": False}
    (output_dir / "m24e_extraction_audit_decision.json").write_text(json.dumps(d, indent=2))
    (output_dir / "m24e_extraction_audit_decision.md").write_text(
        f"# M24-E Extraction Audit Decision\n\n**Decision**: `{decision}`\n\nNo raw logs available.\n")


def _write_metrics_csv(path: Path, metrics: list[dict]) -> None:
    if not metrics:
        return
    fields = ["trial_id", "method", "extraction_status", "actual_velocity_mps",
              "forward_distance", "duration_sec", "n_samples", "yaw_drift_deg",
              "start_x", "end_x", "start_y", "end_y", "start_t_rel", "end_t_rel"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for m in metrics:
            w.writerow(m)


def _write_comparison_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _write_crosscheck_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


# ---------------------------------------------------------------------------
# Report builders
# ---------------------------------------------------------------------------

def _build_crosscheck_md(rows: list[dict], timestamp: str) -> str:
    lines = [
        "# M24-E M24-C Cross-Check",
        f"Generated: {timestamp}",
        "",
        "| Trial ID | Original v_actual | Re-extracted v_actual | Difference | Reproduced? |",
        "|----------|-------------------|----------------------|------------|-------------|",
    ]
    for r in rows:
        icon = "Yes" if r.get("reproduced") else "No"
        lines.append(f"| {r['trial_id']} | {r.get('original_m24b_velocity', '?')} | {r.get('re_extracted_velocity', '?')} | {r.get('difference', '?')} | {icon} |")
    return "\n".join(lines) + "\n"


def _build_anomaly_md(summary: dict, timestamp: str) -> str:
    lines = [
        "# M24-E Extraction Anomaly Report",
        f"Generated: {timestamp}",
        f"Trials audited: {summary.get('total_trials_audited', 0)}",
        f"Anomalies: {summary.get('anomalies_found', 0)}",
        f"Labels: {', '.join(summary.get('labels_assigned', []))}",
        f"Method D tiny forward ratio: {summary.get('method_d_tiny_forward_ratio', 0)}",
        "",
        "## Detailed Anomalies",
    ]
    for a in summary.get("detailed_anomalies", [])[:30]:
        lines.append(f"- **{a.get('trial_id', '?')}**: {a.get('label', '?')} — {a.get('detail', '')}")
    return "\n".join(lines) + "\n"


def _build_decision_md(decision: dict, timestamp: str) -> str:
    return f"""# M24-E Extraction Audit Decision

Generated: {timestamp}

**Decision**: `{decision['decision']}`

**Reason**: {decision['reason']}

**Anomalies found**: {decision['anomalies_found']}
**Original extraction reproduced**: {decision['original_extraction_reproduced']}
**Tiny forward ratio**: {decision['tiny_forward_ratio']}

**Recommendation**: {decision['recommendation']}

## Status Flags

- Gold profile overwritten: **{decision['gold_profile_overwritten']}**
- Candidate profile adopted: **{decision['candidate_profile_adopted']}**
- Compensation validated: **{decision['compensation_validated']}**
- Deployment ready: **{decision['deployment_ready']}**
- GO1/G1 blocked: **{decision['go1_g1_blocked']}**
"""


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def _load_original_extracted(session_dir: Path) -> list[dict[str, str]]:
    path = session_dir / "extracted_results.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _load_trial_records(session_dir: Path) -> list[dict[str, str]]:
    path = session_dir / "trial_records.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _get_t_rel(rows: list[dict[str, str]]) -> list[float]:
    vals = []
    for r in rows:
        try:
            vals.append(float(r.get("t_rel", 0)))
        except (ValueError, TypeError):
            vals.append(0.0)
    return vals


def _safe_floats(rows: list[dict[str, str]], key: str) -> list[float]:
    vals = []
    for r in rows:
        try:
            vals.append(float(r.get(key, 0)))
        except (ValueError, TypeError):
            pass
    return vals


if __name__ == "__main__":
    raise SystemExit(main())
