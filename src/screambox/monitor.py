import asyncio
import pathlib
from typing import *

import aiohttp
import click

import screambox.sounds
from screambox.model import Incident
from screambox.player import Alarm, ScreamPlayer

BASE_URL = "https://europe-west2-screambox.cloudfunctions.net/incidents"
USER_ID = "4c7d513e-7567-4040-9ecd-21756c94a722"

alarm_task: Optional[asyncio.Task] = None


class ScreamBox:
    def __init__(
            self,
            session: aiohttp.ClientSession,
            player: ScreamPlayer,
            waiting_poll: float,
            triggered_poll: float,
            user_id: str,
    ):
        """
        Monitor for incidents and raise the alarm when open incidents are encountered.

        Args:
            session: HTTP session used to poll the cloud API.
            player: Player preloaded with alarm sounds.
            waiting_poll: Interval in seconds between polling for new incidents.
            triggered_poll: Interval in seconds between polling for incident closures.
            user_id: User ID returned from the ScreamBox cloud API when registering a webhook.
        """
        self.session = session
        self.alarm_task: Optional[asyncio.Task] = None
        self.player = player
        self.waiting_poll = waiting_poll
        self.triggered_poll = triggered_poll
        self.user_id = user_id

    async def get_open_incidents(self) -> list[Incident]:
        """
        Retrieve open incidents from the ScreamBox cloud API.

        Returns:
            List of open, unacknowledged incidents.
        """
        async with self.session.get(BASE_URL, params={"user": self.user_id}) as response:
            json = await response.json()
            return [Incident(**i) for i in json["open_incidents"]]

    async def ensure_alarm_playing(self):
        """If the alarm isn't playing, start it."""
        await self.player.start()

    async def ensure_alarm_stopped(self):
        """If the alarm isn't stopped, stop it."""
        await self.player.stop()

    async def run(self):
        """
        Enter an infinite loop monitoring for open or closed incidents and starting or stopping the alarms as necessary.
        """
        while True:
            open_incidents = await self.get_open_incidents()
            if open_incidents:
                print("Alarm is triggered")
                await self.ensure_alarm_playing()
                poll_interval = self.triggered_poll
            else:
                print("Alarm is stopped")
                await self.ensure_alarm_stopped()
                poll_interval = self.waiting_poll

            await asyncio.sleep(poll_interval)


async def main(user_id: str, waiting_poll: float, triggered_poll: float):
    async with aiohttp.ClientSession() as session:

        sounds_basedir = pathlib.Path(screambox.sounds.__file__).parent
        alert = Alarm(sounds_basedir / "alert.mp3", 0)
        scream = Alarm(sounds_basedir / "scream.mp3", 10)

        player = ScreamPlayer([alert, scream])

        box = ScreamBox(session, player, waiting_poll, triggered_poll, user_id)
        await box.run()


@click.command
@click.argument("user-id", type=str)
@click.option(
    "--waiting-poll",
    type=float,
    default=5.0,
    help="Interval in seconds between polling for new incidents."
)
@click.option(
    "--triggered-poll",
    type=float,
    default=1.0,
    help="Interval in seconds between polling for incident closure."
)
def start(*args, **kwargs):
    """
    Begin monitoring for PagerDuty events.

    Arguments:
        USER-ID: The user ID given when the PagerDuty webhook key was registered with the ScreamBox cloud service.
    """
    asyncio.run(main(*args, **kwargs))


if __name__ == "__main__":
    start()
