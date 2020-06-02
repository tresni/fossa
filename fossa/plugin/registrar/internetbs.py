from fossa.plugin.registrar import Registrar

import click
from dateutil.parser import parse

# https://internetbs.net/internet-bs-api.pdf


class Internetbs(Registrar):
    def __init__(self, api_key, password, url="https://api.internet.bs", cache=600, **kwargs):
        self.name = self.api_key = api_key
        self.password = password
        self.url = url
        super().__init__(cache=cache, **kwargs)

    def list(self):
        # NSList may be good at some point
        response = self.request('Domain/List', CompactList="no", ReturnFields="PrivateWhois,Expiration,RegistrarLock,AutoRenewal")
        obj = response.json()
        if obj['status'] == 'FAILURE':
            self.error(obj['message'])
            return []

        for d in obj["domain"]:
            yield {
                "domain": d["name"],
                "expire": parse(d["expiration"]),
                "privacy": True if d["privatewhois"] == "FULL" else False,
                "transferAllowed": True if d["registrarlock"] == "enabled" else False,
                "autoRenew": True if d["autorenewal"] == "YES" else False,
                "registrar": self
            }
        return []

    def request(self, path, *args, **kwargs):
        return self.session.post(
            "{}/{}".format(self.url, path),
            data={
                "ApiKey": self.api_key,
                "Password": self.password,
                "ResponseFormat": "JSON",
                **kwargs
            })
