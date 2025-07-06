import sys
import re
from random import randint
import pyqtgraph as pg

# A regular expression, to extract the % complete.
progress_re = re.compile(r"fps=([\d\.]+)")

ssim_pattern = re.compile(r"n:(\d+) Y:(\d+\.\d+) U:(\d+\.\d+) V:(\d+\.\d+) All:(\d+\.\d+)")

psnr_pattern = re.compile(r"n:(\d+) mse_avg:\d+\.\d+ mse_y:\d+\.\d+ mse_u:\d+\.\d+ mse_v:\d+\.\d+ psnr_avg:(\S+) psnr_y:(\S+) psnr_u:(\S+) psnr_v:(\S+)")



def parse_ssim_values(output):
    """
    Extrait les valeurs SSIM de la sortie FFmpeg.
    Retourne un dictionnaire avec les valeurs frame, Y, U, V, All et info.
    """
    m = ssim_pattern.search(output)
    if m:

       
            
        return {
            'frame': int(m.group(1)),
            'Y': float(m.group(2)),
            'U': float(m.group(3)),
            'V': float(m.group(4)), 
            'All': float(m.group(5)),
        }
    return None


def parse_psnr_values(output):
    """
    Extract PSNR values from FFmpeg output.
    returns a dictionary with frame, Y, U, V, All values. It cap the maximum value to 100, because if video are identical, the PSNR is infinite.
    """
    m = psnr_pattern.search(output)
    if m:
        return {
            'frame': int(m.group(1)),
            'Y': float(m.group(3)) if float(m.group(3)) != float('inf') else float(100),
            'U': float(m.group(4)) if float(m.group(4)) != float('inf') else float(100),
            'V': float(m.group(5)) if float(m.group(5)) != float('inf') else float(100), 
            'All': float(m.group(2)) if float(m.group(2)) != float('inf') else float(100),
        }
    return None


def simple_fps_parser(output):
    """
    Matches lines using the progress_re regex,
    returning a single integer for the % progress.
    """
    m = progress_re.search(output)
    if m:
        pc_complete = m.group(1)
        return float(pc_complete)
    