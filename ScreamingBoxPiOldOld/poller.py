import requests


class Poller:

    def poll_api(self):
        response = requests.get("http://34.247.181.217:8000/poll")
        is_open = response.json()['is_open']
        return is_open
