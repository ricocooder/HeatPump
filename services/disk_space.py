"""
Disk space monitoring for the Raspberry Pi SD card.

Runs ``df -h /`` and parses the result to report usage of the root filesystem.
Used on the /raspberrypi settings page to warn when the SD card is nearly full.
A full SD card would cause SQLite writes to fail silently, so early warning matters.
"""

import logging
import os

log = logging.getLogger(__name__)


def get_df() -> list:
    """
    Run ``df -h /`` and return the data columns of the root filesystem row.

    Returns:
        list[str]: Up to 6 fields from the df output row:
                   [Filesystem, Size, Used, Avail, Use%, Mounted].
                   Returns an empty list if the command fails.
    """
    try:
        df = os.popen("df -h /")
        lines = df.readlines()
        df.close()
        if len(lines) >= 2:
            return lines[1].split()[0:6]  # skip header (lines[0])
    except Exception as e:
        log.error("df failed: %s", e)
    return []


def check_disk_space(threshold_percent: int = 80) -> tuple:
    """
    Check whether root filesystem usage exceeds a warning threshold.

    Args:
        threshold_percent: Alert if used% >= this value. Default 80%.

    Returns:
        tuple[list, bool]: (df_fields, is_full)
            - df_fields: raw df output fields (may be empty list on error)
            - is_full: True if usage is at or above threshold_percent
    """
    data = get_df()
    if not data:
        return data, False
    try:
        # data[4] is the Use% column, e.g. '72%' — strip '%' before int conversion
        used_pct = int(data[4].replace('%', ''))
        return data, used_pct >= threshold_percent
    except (IndexError, ValueError) as e:
        log.error("Could not parse disk usage: %s", e)
        return data, False
