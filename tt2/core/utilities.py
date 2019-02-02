"""
utilities.py

Any utility or backing functions can be placed here and imported when needed.
"""
from tt2.external.imagesearch import *
from tt2.core.constants import (
    STATS_DURATION_RE, STATS_LOOKUP_MULTIPLIER, STATS_TIMEDELTA_STR,
    LOGGER_NAME, LOGGER_FORMAT, LOGGER_FILE_NAME
)

from string import Template, Formatter
from pyautogui import *

import datetime
import logging
import time
import math

logger = logging.getLogger(LOGGER_NAME)


def sleep(seconds):
    """Wrap the time.sleep method to allow for logging the time to sleep for."""
    logger.debug("sleeping for {seconds} second(s)".format(seconds=seconds))
    time.sleep(seconds)


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(timedelta, fmt=STATS_TIMEDELTA_STR):
    """Format a timedelta object in the given format."""
    f = Formatter()
    d = {}
    lst = {"D": 86400, "H": 3600, "M": 60, "S": 1}
    k = map(lambda x: x[1], list(f.parse(fmt)))
    remainder = int(timedelta.total_seconds())

    for i in ("D", "H", "M", "S"):
        if i in k and i in lst.keys():
            d[i], remainder = divmod(remainder, lst[i])

    for key, value in d.items():
        if value < 10 and "D" not in key:
            d[key] = "0" + str(value)

    return f.format(fmt, **d)


def convert(value):
    """Attempt to convert a given value into its appropriate integer value."""
    try:
        return float(value)
    except ValueError:
        pass
    except TypeError:
        return value

    unit = value[-1]
    try:
        number = float(value[:-1])
    except ValueError:
        number = None

    if not number:
        return value

    if unit in STATS_LOOKUP_MULTIPLIER:
        return STATS_LOOKUP_MULTIPLIER[unit] * number

    return number


def diff(old, new):
    """
    Determine the difference between values. The accepted values here may be
    datetime objects, floats, or integers.
    """
    if isinstance(old, (int, float)) and isinstance(new, (int, float)):
        value = new - old

        # Infinity/NAN values should be dealt with by just returning a readable string.
        # Users can manually audit the changes since they're exponential.
        if math.isnan(value) or math.isinf(value):
            return "TOO BIG"

        try:
            return int(value)
        except ValueError:
            return value

    # Maybe a date is being diffed?
    if isinstance(old, str) and isinstance(new, str):
        try:
            old_params = {
                name: float(param) for name, param in STATS_DURATION_RE.match(old).groupdict().items() if param
            }
            new_params = {
                name: float(param) for name, param in STATS_DURATION_RE.match(new).groupdict().items() if param
            }

            old_td = datetime.timedelta(**old_params)
            new_td = datetime.timedelta(**new_params)

            delta = new_td - old_td
            return strfdelta(delta)

        # Gracefully exit and return None, treated as null in JSON.
        except Exception:
            return "ERROR DIFFING"

    return None


def gen_offset(point, amount):
    """Add some offset to a given point."""
    if amount == 0:
        return point

    rand_x = random.randint(-amount, amount)
    rand_y = random.randint(-amount, amount)

    return point[0] + rand_x, point[1] + rand_y


def click_on_point(point, clicks=1, interval=0, button="left", pause=0.0, offset=5):
    """Click on the specified X, Y value based on the point passed along as a parameter."""
    if offset != 0:
        point = gen_offset(point, offset)

    logger.debug(
        "{button} clicking {point} on screen {clicks} time(s) with {interval} interval and {pause} pause".format(
            button=button, point=point, clicks=clicks, interval=interval, pause=pause
        )
    )
    click((point[0], point[1]), clicks=clicks, interval=interval, button=button, pause=pause)


def click_on_image(image=None, pos=None, button="left", pause=0.0):
    """Click on the specified image on the screen."""
    logger.debug(
        "{button} clicking on {image} located at {pos} with {pause}s pause".format(
            button=button, image=image, pos=pos, pause=pause
        )
    )
    click_image(image=image, pos=pos, action=button, timestamp=0, pause=pause)


def drag_mouse(start, end, button="left", duration=0.3, pause=0.5, tween=linear, quick_stop=None):
    """Drag the mouse from the starting position, to the end position."""
    logger.debug(
        "{button} clicking and dragging mouse from {start} to {end} over {duration}s with quick stop {quick}".format(
            button=button, start=start, end=end, duration=duration, quick="enabled" if quick_stop else "disabled"
        )
    )
    moveTo(start[0], start[1])

    # Determine pause amount tween. Tweening may be useful for specific actions
    # since dragging may continue after drag is finished.
    pause = pause if not quick_stop else 0

    dragTo(end[0], end[1], duration=duration, button=button, pause=pause, tween=tween)

    if quick_stop:
        click_on_point((quick_stop[0], quick_stop[1]), pause=0.5, offset=0)


def in_transition_func(*args, max_loops):
    """Directly call this function to perform the transition state check."""
    _self = args[0]
    loops = 0
    while True:
        # If an ad screen is opened and it happened to be missed during the collect_ad check, a manual
        # check is also performed here and the ad is collected / declined directly.
        ad = _self.grabber.search(_self.images.collect_ad, bool_only=True)
        if ad:
            if _self.config.ENABLE_PREMIUM_AD_COLLECT:
                _self.logger.info("accepting premium ad through transition check")
                click_on_point(_self.locs.collect_ad)
            else:
                _self.logger.info("declining premium ad through transition check")
                click_on_point(_self.locs.no_thanks)
            break

        exit_panel = _self.grabber.search(_self.images.exit_panel, bool_only=True)
        if exit_panel:
            break
        settings = _self.grabber.search(_self.images.settings, bool_only=True)
        if settings:
            break
        clan_ready = _self.grabber.search(_self.images.clan_battle_ready, bool_only=True)
        if clan_ready:
            break
        clan_unready = _self.grabber.search(_self.images.clan_no_battle, bool_only=True)
        if clan_unready:
            break
        fight_boss = _self.grabber.search(_self.images.fight_boss, bool_only=True)
        if fight_boss:
            break
        leave_boss = _self.grabber.search(_self.images.leave_boss, bool_only=True)
        if leave_boss:
            break

        # Clicking the top of the screen in case of a transition taking place due to something being
        # present on the screen that requires clicking.
        click_on_point(_self.master_locs["screen_top"], clicks=3, pause=0.5)

        _self.logger.debug("in a transition? waiting 1s before continuing")
        sleep(1)

        loops += 1
        if loops == max_loops:
            # In this case, the game may of broke? A crash may of occurred. It's safe to attempt to restart the
            # game at this point.
            _self.logger.error("unable to resolve transition state of game, attempting to restart game.")
            _self.restart_game()

            # Is the restarted / rescued from crash?
            if _self.grabber.search(_self.images.settings, bool_only=True):
                _self.logger.info("game has been successfully restarted")

            _self.logger.error("unable to restart game, terminating bot now")
            _self.terminate()
            break


def make_logger(config):
    """Grab the logging instance that will be used throughout bot runtime."""
    log_formatter = logging.Formatter(LOGGER_FORMAT)
    _logger = logging.getLogger(LOGGER_NAME)

    file_handler = logging.FileHandler(LOGGER_FILE_NAME)
    file_handler.setFormatter(log_formatter)
    _logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    _logger.addHandler(console_handler)

    _logger.setLevel(config.LOGGING_LEVEL)

    return _logger