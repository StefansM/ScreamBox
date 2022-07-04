import asyncio
import dataclasses
import pathlib
from typing import List, Optional


@dataclasses.dataclass
class Alarm:
    # Audio file to play.
    file: pathlib.Path
    # Delay before playback starts.
    delay: float


async def run(*args: str, delay: Optional[float] = None):
    """
    Asynchronously run a process, optionally waiting for `delay` seconds.

    When this coroutine is cancelled, the underlying process is terminated.

    Args:
        *args: Executable and arguments.
        delay: Delay seconds to wait before running the executable.
    """
    if delay:
        await asyncio.sleep(delay)

    proc = await asyncio.create_subprocess_exec(*args)
    try:
        await proc.wait()
    except asyncio.CancelledError:
        print(f"Cancelled: terminating subprocess: {args}")
        proc.terminate()
        raise


class ScreamPlayer:
    def __init__(self, alarms: List[Alarm]):
        """
        When triggered, play several alarms at once.
        Args:
            alarms: Alarms to be played.
        """
        self.alarms = alarms
        self.alarm_task: Optional[asyncio.Task] = None

    async def start(self):
        if not self.alarm_task:
            tasks = [
                run("mpg123", "-q", "--loop", "-1", str(alarm.file), delay=alarm.delay)
                for alarm in self.alarms
            ]
            self.alarm_task = asyncio.gather(*tasks, return_exceptions=True)

    async def stop(self):
        if self.alarm_task:
            try:
                self.alarm_task.cancel()
                await self.alarm_task
            except asyncio.CancelledError:
                pass
