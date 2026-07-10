import logging
import threading
import json
import os
import sys
import traceback
import schedule
from time import sleep

import modules.config as cfg
from modules.radio import playRadio, killMusic

_WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
_ALARM_DURATION_SEC = 3600

_scheduler = schedule.Scheduler()
_lock = threading.Lock()
_stop_timer = None

_state = {
    'enabled': False,
    'hour': 6,
}

def _state_path():
    return os.path.join(cfg.basePath, 'alarm_state.json')

def _load_state():
    path = _state_path()
    try:
        if os.path.isfile(path):
            with open(path) as f:
                data = json.load(f)
            _state['enabled'] = bool(data.get('enabled', _state['enabled']))
            _state['hour'] = int(data.get('hour', _state['hour']))
    except Exception:
        logging.error("Unable to read alarm state, using defaults")

def _save_state():
    try:
        with open(_state_path(), 'w') as f:
            json.dump(_state, f)
    except Exception:
        logging.error("Unable to persist alarm state")

def _reschedule():
    _scheduler.clear('alarm')
    if _state['enabled']:
        time_str = "%02d:00" % _state['hour']
        for day in _WEEKDAYS:
            getattr(_scheduler.every(), day).at(time_str).do(_triggerAlarm).tag('alarm')
        logging.info("Alarm scheduled for %s on workdays (Mon-Fri)", time_str)
    else:
        logging.info("Alarm disabled")

def _triggerAlarm():
    global _stop_timer
    logging.info("Alarm triggered - starting radio")
    try:
        killMusic()
        threading.Thread(target=playRadio, args=('ns',), daemon=True).start()
        if _stop_timer is not None:
            _stop_timer.cancel()
        _stop_timer = threading.Timer(_ALARM_DURATION_SEC, _stopAlarm)
        _stop_timer.daemon = True
        _stop_timer.start()
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error("Alarm start error: %s", traceback.format_tb(exc_traceback))

def _stopAlarm():
    logging.info("Alarm timeout reached - stopping radio")
    killMusic()

def init():
    _load_state()
    with _lock:
        _reschedule()

def runAlarmSched():
    logger = logging.getLogger(threading.current_thread().name)
    logger.info("Starting alarm scheduler")
    init()
    while True:
        _scheduler.run_pending()
        sleep(1)

def setHour(hour):
    hour = int(hour)
    if hour < 0 or hour > 23:
        raise ValueError("hour must be between 0 and 23")
    with _lock:
        _state['hour'] = hour
        _save_state()
        _reschedule()
    return getStatus()

def enableAlarm():
    with _lock:
        _state['enabled'] = True
        _save_state()
        _reschedule()
    return getStatus()

def disableAlarm():
    with _lock:
        _state['enabled'] = False
        _save_state()
        _reschedule()
    return getStatus()

def getStatus():
    return dict(_state)
