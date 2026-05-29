import logging
import subprocess
import shlex
import threading
from urllib.parse import urlparse
import modules.config as cfg
from modules.oled_display import OledDisplay

_ALLOWED_SCHEMES = {'http', 'https', 'rtsp', 'mms'}

def _is_valid_stream_url(url):
    try:
        p = urlparse(url)
        return p.scheme in _ALLOWED_SCHEMES and bool(p.netloc)
    except Exception:
        return False

def playRadio(id):
    if id == 'ns':
        vol, url = cfg.radio_1_vol, cfg.radio_1
    elif id == '357':
        vol, url = cfg.radio_2_vol, cfg.radio_2
    else:
        logging.warning("playRadio: unknown id %s", id)
        return
    subprocess.call(
        "amixer -c 1 set Speaker " + vol,
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    mpv_cmd = "mpv --vid=no --cache=yes --demuxer-max-bytes=5MiB " + shlex.quote(url)
    logging.info("Trying to run: " + mpv_cmd)
    try:
        proc = subprocess.Popen(
            mpv_cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1)
        _watch_icy_titles(proc)
        proc.wait()
    except Exception as e:
        logging.error("Unable to play radio: %s", e)

def _watch_icy_titles(proc):
    def _read(p):
        for line in p.stdout:
            if 'icy-title' in line.lower():
                title = line.split(':', 1)[-1].strip()
                logging.info("ICY title: %s", title)
                OledDisplay.get_instance().show_message(title, duration=10)
    threading.Thread(target=_read, args=(proc,), daemon=True).start()

def playStream(stream):
    if not _is_valid_stream_url(stream):
        logging.warning("playStream: invalid or missing URL, skipping: %s", stream)
        return
    subprocess.call(
        "amixer -c 1 set Speaker " + cfg.radio_1_vol,
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    mpv_cmd = "mpv --vid=no --cache=yes --demuxer-max-bytes=5MiB " + shlex.quote(stream)
    logging.info("Trying to run: " + mpv_cmd)
    try:
        proc = subprocess.Popen(
            mpv_cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1)
        _watch_icy_titles(proc)
        proc.wait()
    except Exception as e:
        logging.error("Unable to play stream: %s", e)

def killMusic():
    command = "killall -9 mplayer" #command to be executed
    try:
        res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        logging.info("Unable to stop playing mplayer")
    command = "killall -9 mpv" #command to be executed
    try:
        res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        logging.error("Unable to stop playing mpv")
    return
def playLulaby(id):
    command = "amixer -c 1 set Speaker"
    if id == '1':
        command += " "+cfg.song_1_vol+" && mplayer "+cfg.song_1
    elif id == '2':
        command += " "+cfg.song_2_vol+" && mplayer "+cfg.song_2
    try:
        res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        logging.error("Unable to play lulaby")
    return
