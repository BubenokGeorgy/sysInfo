import re
import time
from contextlib import suppress
from datetime import timedelta
from subprocess import PIPE, run

from entry import Entry
from exceptions import SysInfoException


class Uptime(Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        uptime_seconds = int(self._get_uptime_delta().total_seconds())

        days, uptime_seconds = divmod(uptime_seconds, 86400)
        hours, uptime_seconds = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(uptime_seconds, 60)

        self.value = {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds}

    def _get_uptime_delta(self) -> timedelta:
        try:
            return self._proc_file_uptime()
        except OSError:
            pass

        try:
            return self._clock_uptime()
        except RuntimeError:
            pass

        return self._parse_uptime_cmd()

    @staticmethod
    def _proc_file_uptime() -> timedelta:
        with open("/proc/uptime", encoding="ASCII") as f_uptime:
            return timedelta(seconds=float(f_uptime.read().split()[0]))

    @staticmethod
    def _clock_uptime() -> timedelta:
        for clock in ("CLOCK_BOOTTIME", "CLOCK_UPTIME"):
            with suppress(AttributeError):
                return timedelta(seconds=time.clock_gettime(getattr(time, clock)))

        raise RuntimeError

    def _parse_uptime_cmd(self) -> timedelta:
        try:
            uptime_output = run("uptime", env={"LANG": "C"}, stdout=PIPE, stderr=PIPE, check=True)
        except FileNotFoundError as error:
            raise SysInfoException("Couldn't find `uptime` command on this system.") from error

        if uptime_output.stderr:
            for line in uptime_output.stderr.splitlines():
                self._logger.warning("[uptime]: %s", line.decode())

        uptime_match = re.search(
            rb"""
            up\s+?             # match the `up` preceding the uptime (anchor the start of the regex)
            (?:                # non-capture group for days section.
               (?P<days>       # 'days' named capture group, captures the days digits.
                  \d+?
               )
               \s+?            # match whitespace,
               days?           #   'day' or 'days',
               [,\s]+?         #   then a comma (if present) followed by more whitespace.
            )?                 # match the days non-capture group 0 or 1 times.
            (?:                # non-capture group for hours & minutes section.
               (?:             # non-capture group for just hours section.
                  (?P<hours>   # 'hours' named capture group, captures the hours digits.
                     \d+?
                  )
                  (?:          # non-capture group for hours:minutes colon or 'hrs' text...
                     :         #   i.e. hours followed by either a single colon
                     |         #   OR
                     \s+?      #   1 or more whitespace chars non-greedily,
                     hrs?      #   followed by 'hr' or 'hrs'.
                  )
               )?              # match the hours non-capture group 0 or 1 times.
               (?:             # non-capture group for minutes section.
                  (?P<minutes> # 'minutes' named capture group, captures the minutes digits.
                     \d+?
                  )
                  (?:          # non-capture group for 'min' or 'mins' text.
                     \s+?      # match whitespace,
                     mins?     #   followed by 'min' or 'mins'.
                  )?           # match the text 0 or 1 times (0 times is for the hh:mm format case).
                  (?!          # negative lookahead group
                     \d+       #   this prevents matching seconds digits as minutes...
                     \s+?      #   since we only non-greedily match minutes digits earlier.
                     secs?     #   here's the part that matches the 'sec' or 'secs' text.
                  )            # the minutes group is discarded if this lookahead matches!
               )?              # match the minutes non-capture group 0 or 1 times.
            )?                 # match the entire hours & minutes non-capture group 0 or 1 times.
            (?:                # non-capture group for seconds.
               (?P<seconds>    # 'seconds' named capture group, captures the seconds digits.
                  \d+?
               )
               \s+?            # match whitespace,
               secs?           #  then 'sec' or 'secs'.
            )?                 # match the seconds non-capture group 0 or 1 times.
            [,\s]*?            # after the groups, match a comma and/or whitespace 0 or more times,
            \d+?               #   one or more digits for the user count,
            \s+?               #   whitespace between the user count and the text 'user',
            user               #   and the text 'user' (to anchor the end of the expression).
            """,
            uptime_output.stdout,
            re.VERBOSE,
        )
        if not uptime_match:
            raise SysInfoException("Couldn't parse `uptime` output.")

        uptime_args = uptime_match.groupdict()
        return timedelta(
            days=int(uptime_args.get("days") or 0),
            hours=int(uptime_args.get("hours") or 0),
            minutes=int(uptime_args.get("minutes") or 0),
            seconds=int(uptime_args.get("seconds") or 0),
        )

    def output(self, output) -> None:
        days = self.value["days"]
        hours = self.value["hours"]
        minutes = self.value["minutes"]

        uptime = ""
        if days:
            uptime += str(days) + " day"
            if days > 1:
                uptime += "s"

            if hours or minutes:
                if bool(hours) != bool(minutes):
                    uptime += " and "
                else:
                    uptime += ", "

        if hours:
            uptime += str(hours) + " hour"
            if hours > 1:
                uptime += "s"

            if minutes:
                uptime += " and "

        if minutes:
            uptime += str(minutes) + " minute"
            if minutes > 1:
                uptime += "s"
        elif not days and not hours:
            uptime = "< 1 minute"

        output.append(self.name, uptime)
