"""Static visualization artifacts for K1 measurement readability."""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path
from typing import Any


def _ensure_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _try_matplotlib() -> Any:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        return plt
    except ModuleNotFoundError:
        return None


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def _write_png(path: Path, width: int, height: int, pixels: bytearray) -> str:
    rows = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))
    payload = b"\x89PNG\r\n\x1a\n"
    payload += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    payload += _png_chunk(b"IDAT", zlib.compress(rows))
    payload += _png_chunk(b"IEND", b"")
    path.write_bytes(payload)
    return str(path)


def _set_pixel(pixels: bytearray, width: int, height: int, x: int, y: int, color: tuple[int, int, int]) -> None:
    if 0 <= x < width and 0 <= y < height:
        index = (y * width + x) * 3
        pixels[index : index + 3] = bytes(color)


def _draw_line(
    pixels: bytearray,
    width: int,
    height: int,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
) -> None:
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    error = dx + dy
    while True:
        for ox in range(-1, 2):
            for oy in range(-1, 2):
                _set_pixel(pixels, width, height, x0 + ox, y0 + oy, color)
        if x0 == x1 and y0 == y1:
            break
        doubled = 2 * error
        if doubled >= dy:
            error += dy
            x0 += sx
        if doubled <= dx:
            error += dx
            y0 += sy


def _fallback_line_plot(series: list[tuple[list[float], list[float], tuple[int, int, int]]], output_path: Path) -> str:
    width, height = 640, 420
    margin = 48
    pixels = bytearray([255, 255, 255] * width * height)

    for x in range(margin, width - margin):
        _set_pixel(pixels, width, height, x, height - margin, (80, 80, 80))
    for y in range(margin, height - margin):
        _set_pixel(pixels, width, height, margin, y, (80, 80, 80))

    xs = [value for x_values, _, _ in series for value in x_values]
    ys = [value for _, y_values, _ in series for value in y_values]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    if x_min == x_max:
        x_max = x_min + 1.0
    if y_min == y_max:
        y_max = y_min + 1.0

    def point(x_value: float, y_value: float) -> tuple[int, int]:
        x = margin + int((x_value - x_min) / (x_max - x_min) * (width - 2 * margin))
        y = height - margin - int((y_value - y_min) / (y_max - y_min) * (height - 2 * margin))
        return x, y

    for x_values, y_values, color in series:
        points = [point(x_value, y_value) for x_value, y_value in zip(x_values, y_values)]
        for first, second in zip(points, points[1:]):
            _draw_line(pixels, width, height, first, second, color)
        for x, y in points:
            _draw_line(pixels, width, height, (x - 3, y), (x + 3, y), color)
            _draw_line(pixels, width, height, (x, y - 3), (x, y + 3), color)

    return _write_png(output_path, width, height, pixels)


def load_velocity_profile(profile_path: str | Path) -> list[dict[str, Any]]:
    """Load `velocity_profile` from a processed environment profile JSON."""

    profile = json.loads(Path(profile_path).read_text(encoding="utf-8"))
    return list(profile.get("velocity_profile", []))


def _records(data: Any) -> list[dict[str, Any]]:
    if data is None:
        return []
    if hasattr(data, "to_dict"):
        return data.to_dict("records")
    return list(data)


def _has_columns(rows: list[dict[str, Any]], columns: set[str]) -> bool:
    return bool(rows) and all(column in rows[0] for column in columns)


def _column(rows: list[dict[str, Any]], name: str) -> list[float]:
    return [float(row[name]) for row in rows]


def generate_command_vs_actual_velocity_plot(data: Any, output_dir: str | Path) -> str | None:
    required = {"vx_cmd_mps", "vx_actual_mean_mps"}
    rows = _records(data)
    if not _has_columns(rows, required):
        return None

    output = _ensure_output_dir(output_dir) / "velocity_error_plot.png"
    x = _column(rows, "vx_cmd_mps")
    y = _column(rows, "vx_actual_mean_mps")
    plt = _try_matplotlib()
    if plt is None:
        return _fallback_line_plot([(x, x, (90, 90, 90)), (x, y, (37, 99, 235))], output)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(x, x, linestyle="--", color="0.45", label="ideal")
    ax.plot(x, y, marker="o", color="#2563eb", label="measured mean")
    if "vx_actual_std_mps" in rows[0]:
        ax.errorbar(x, y, yerr=_column(rows, "vx_actual_std_mps"), fmt="none", color="#2563eb", alpha=0.45)
    ax.set_xlabel("commanded vx (m/s)")
    ax.set_ylabel("actual vx mean (m/s)")
    ax.set_title("Command vs Actual Forward Velocity")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return str(output)


def generate_speed_gain_plot(data: Any, output_dir: str | Path) -> str | None:
    required = {"vx_cmd_mps", "speed_gain_mean"}
    rows = _records(data)
    if not _has_columns(rows, required):
        return None

    output = _ensure_output_dir(output_dir) / "speed_gain_plot.png"
    x = _column(rows, "vx_cmd_mps")
    y = _column(rows, "speed_gain_mean")
    plt = _try_matplotlib()
    if plt is None:
        return _fallback_line_plot([(x, [1.0 for _ in x], (90, 90, 90)), (x, y, (5, 150, 105))], output)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.axhline(1.0, linestyle="--", color="0.45", label="ideal gain")
    ax.plot(x, y, marker="o", color="#059669", label="speed gain")
    if "speed_gain_std" in rows[0]:
        ax.errorbar(x, y, yerr=_column(rows, "speed_gain_std"), fmt="none", color="#059669", alpha=0.45)
    ax.set_xlabel("commanded vx (m/s)")
    ax.set_ylabel("speed gain")
    ax.set_title("Speed Gain by Command Speed")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return str(output)


def generate_trial_time_series_plot(data: Any, output_dir: str | Path) -> str | None:
    required = {"timestamp", "vx_cmd", "odom_vx"}
    rows = _records(data)
    if not _has_columns(rows, required):
        return None

    output = _ensure_output_dir(output_dir) / "trial_timeseries_plot.png"
    timestamp = _column(rows, "timestamp")
    vx_cmd = _column(rows, "vx_cmd")
    odom_vx = _column(rows, "odom_vx")
    plt = _try_matplotlib()
    if plt is None:
        return _fallback_line_plot([(timestamp, vx_cmd, (124, 58, 237)), (timestamp, odom_vx, (220, 38, 38))], output)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(timestamp, vx_cmd, label="vx_cmd", color="#7c3aed")
    ax.plot(timestamp, odom_vx, label="odom_vx", color="#dc2626")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("velocity (m/s)")
    ax.set_title("Trial Velocity Time Series")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return str(output)


def generate_drift_plot(data: Any, output_dir: str | Path) -> str | None:
    rows = _records(data)
    if not rows or "timestamp" not in rows[0]:
        return None
    drift_columns = [column for column in ["odom_y", "odom_yaw"] if column in rows[0]]
    if not drift_columns:
        return None

    output = _ensure_output_dir(output_dir) / "drift_plot.png"
    timestamp = _column(rows, "timestamp")
    colors = [(8, 145, 178), (234, 88, 12)]
    plt = _try_matplotlib()
    if plt is None:
        return _fallback_line_plot(
            [(timestamp, _column(rows, column), colors[index % len(colors)]) for index, column in enumerate(drift_columns)],
            output,
        )
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for column in drift_columns:
        ax.plot(timestamp, _column(rows, column), label=column)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("drift signal")
    ax.set_title("Lateral and Yaw Drift Signals")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return str(output)


def generate_measurement_plots(
    velocity_profile: Any = None,
    trial_timeseries: Any = None,
    output_dir: str | Path = "outputs/plots",
) -> dict[str, str | None]:
    """Generate all available static plots and skip missing inputs gracefully."""

    velocity_profile = velocity_profile if velocity_profile is not None else []
    trial_timeseries = trial_timeseries if trial_timeseries is not None else []
    return {
        "velocity_error_plot": generate_command_vs_actual_velocity_plot(velocity_profile, output_dir),
        "speed_gain_plot": generate_speed_gain_plot(velocity_profile, output_dir),
        "trial_timeseries_plot": generate_trial_time_series_plot(trial_timeseries, output_dir),
        "drift_plot": generate_drift_plot(trial_timeseries, output_dir),
    }
