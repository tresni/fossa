from fossa.plugin.registrar import Registrar

from dateutil.parser import parse


class Gandi(Registrar):
    def __init__(self, api_key, **kwargs):
        self.name = self.api_key = api_key
        super().__init__(**kwargs)

    def list(self, **kwargs):
        url = 'https://api.gandi.net/v5/domain/domains'
        response = self.session.get(url, headers={
            "Authorization": "Apikey {}".format(self.api_key)
        })

        if response.status_code != 200:
            self.error("Can't get domains from Gandi")
            return

        for domain in response.json():
            yield {
                'domain': domain['fqdn'],
                'id': domain['id'],
                'created': parse(domain['dates']['created_at']),
                'expire': parse(domain['dates']['registry_ends_at'], ignoretz=True),
                'privacy': None,
                'transferAllowed': True if 'clientTransferProhibited' in domain['status'] else False,
                'autoRenew': domain['autorenew'],
                'registrar': self
            }
