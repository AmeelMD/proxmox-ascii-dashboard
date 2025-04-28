#!/usr/bin/env python3

import os
import time
import psutil
import socket
import math
import subprocess
from datetime import datetime
from blessed import Terminal

term = Terminal()

# Colors
base_orange = (255, 78, 0)
static_white = (255, 255, 255)

# Functions

def load_logo():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    logo_path = os.path.join(script_dir, "assets", "logo.txt")
    if os.path.exists(logo_path):
        with open(logo_path, "r") as f:
            return f.readlines()
    else:
        return []

def load_cat():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    cat_path = os.path.join(script_dir, "assets", "cat.txt")
    if os.path.exists(cat_path):
        with open(cat_path, "r") as f:
            return f.readlines()
    else:
        return []

def get_hostname():
    return os.uname()[1]

def get_primary_interface():
    for interface, addrs in psutil.net_if_addrs().items():
        if interface == "lo":
            continue
        if any(addr.family == socket.AF_INET for addr in addrs):
            return interface
    return "eth0"

def get_ip_mac(interface):
    ip = mac = "N/A"
    for addr in psutil.net_if_addrs().get(interface, []):
        if addr.family == socket.AF_INET:
            ip = addr.address
        elif addr.family == psutil.AF_LINK:
            mac = addr.address
    return ip, mac

def format_uptime():
    uptime_seconds = int(time.time() - psutil.boot_time())
    minutes, seconds = divmod(uptime_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return days, hours, minutes, seconds

def get_cpu_usage():
    return psutil.cpu_percent(interval=None)

def get_ram_usage():
    mem = psutil.virtual_memory()
    return mem.percent

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.percent

def get_network_usage(interface):
    counters = psutil.net_io_counters(pernic=True).get(interface)
    if counters:
        return counters.bytes_sent, counters.bytes_recv
    return 0, 0

def get_temperature():
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current:
                        return f"{entry.current:.1f}"
    except Exception:
        pass
    return "N/A"

def breathing_brightness(frame_count):
    cycle_frames = 60.0
    brightness = (math.cos(2 * math.pi * (frame_count / cycle_frames)) + 1) / 2
    brightness = 0.2 + 0.6 * brightness
    return brightness

def draw_background(term, brightness):
    r = int(base_orange[0] * brightness)
    g = int(base_orange[1] * brightness)
    b = int(base_orange[2] * brightness)
    bg_color = term.color_rgb(r, g, b)

    for y in range(term.height):
        print(term.move_yx(y, 0) + bg_color + '-' * term.width + term.normal)

def draw_black_box(term, box_top, box_left, box_bottom, box_right):
    black = term.color_rgb(0, 0, 0)
    for y in range(box_top, box_bottom + 1):
        print(term.move_yx(y, box_left) + black + ' ' * (box_right - box_left + 1) + term.normal)

def draw_rounded_border(term, box_top, box_left, box_bottom, box_right):
    border_col = term.color_rgb(*static_white)
    print(term.move_yx(box_top, box_left) + border_col + '╭' + term.normal)
    print(term.move_yx(box_top, box_right) + border_col + '╮' + term.normal)
    print(term.move_yx(box_bottom, box_left) + border_col + '╰' + term.normal)
    print(term.move_yx(box_bottom, box_right) + border_col + '╯' + term.normal)

    for x in range(box_left + 1, box_right):
        print(term.move_yx(box_top, x) + border_col + '─' + term.normal)
        print(term.move_yx(box_bottom, x) + border_col + '─' + term.normal)
    for y in range(box_top + 1, box_bottom):
        print(term.move_yx(y, box_left) + border_col + '│' + term.normal)
        print(term.move_yx(y, box_right) + border_col + '│' + term.normal)
        
def restart_login_prompt():
    try:
        subprocess.run(["systemctl", "restart", "getty@tty1.service"], check=True)
    except Exception as e:
        print(f"Failed to restart login prompt: {e}")

# Main Display Loop

def main():
    interface = get_primary_interface()
    hostname = get_hostname()
    logo_lines = load_logo()
    cat_lines = load_cat()
    frame_count = 0

    with term.fullscreen(), term.hidden_cursor(), term.cbreak():
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")

            cpu = get_cpu_usage()
            ram = get_ram_usage()
            disk = get_disk_usage()
            sent, recv = get_network_usage(interface)
            days, hours, minutes, seconds = format_uptime()
            ip, mac = get_ip_mac(interface)
            temp = get_temperature()

            print(term.home)

            height, width = term.height, term.width

            # Build dashboard content
            lines = []

            for logo_line in logo_lines:
                lines.append(term.white + logo_line.rstrip() + term.normal)

            lines.append("")
            lines.append(term.color_rgb(255, 78, 0) + hostname + term.normal)
            lines.append("")
            lines.append(term.color_rgb(255, 78, 0) + current_time + term.normal)
            lines.append("")

            lines.append(
                f"CPU: {term.color_rgb(255, 78, 0)}{cpu:.1f}%{term.normal}   "
                f"RAM: {term.color_rgb(255, 78, 0)}{ram:.1f}%{term.normal}   "
                f"Disk: {term.color_rgb(255, 78, 0)}{disk:.1f}%{term.normal}"
            )

            uptime_str = (
                f"{term.color_rgb(255, 78, 0)}{days}d{term.normal} "
                f"{term.color_rgb(255, 78, 0)}{hours}h{term.normal} "
                f"{term.color_rgb(255, 78, 0)}{minutes}m{term.normal} "
                f"{term.color_rgb(255, 78, 0)}{seconds}s{term.normal}"
            )
            temp_str = (
                f"{term.color_rgb(255, 78, 0)}{temp}°C{term.normal}" if temp != "N/A" else f"{term.color_rgb(255, 78, 0)}N/A{term.normal}"
            )
            lines.append(f"Uptime: {uptime_str}   Temp: {temp_str}")

            lines.append(
                f"IP: {term.color_rgb(255, 78, 0)}{ip}{term.normal}   "
                f"MAC: {term.color_rgb(255, 78, 0)}{mac}{term.normal}"
            )

            lines.append("")
            lines.append(term.white + "Press any key to exit..." + term.normal)
            lines.append("")
            lines.append("")

            for cat_line in cat_lines:
                lines.append(term.white + cat_line.rstrip() + term.normal)

            # Calculate box size
            raw_content = [term.strip_seqs(line) for line in lines]
            box_content_width = max(len(line) for line in raw_content) + 4
            box_content_height = len(lines) + 2

            box_top = (height - box_content_height) // 2
            box_left = (width - box_content_width) // 2
            box_bottom = box_top + box_content_height
            box_right = box_left + box_content_width

            # Background breathing
            brightness = breathing_brightness(frame_count)
            draw_background(term, brightness)

            # Solid black box
            draw_black_box(term, box_top, box_left, box_bottom, box_right)

            # White border
            draw_rounded_border(term, box_top, box_left, box_bottom, box_right)

            # Print dashboard content
            box_center_x = box_left + (box_right - box_left) // 2
            start_y = box_top + 1

            for idx, line in enumerate(lines):
                y = start_y + idx
                clean_text = line
                line_width = len(term.strip_seqs(clean_text))
                x = box_center_x - (line_width // 2)
                print(term.move_yx(y, x) + clean_text)

            time.sleep(0.5)
            frame_count += 1

            if term.inkey(timeout=0):
                break

if __name__ == "__main__":
    try:
        main()
    finally:
        restart_login_prompt()