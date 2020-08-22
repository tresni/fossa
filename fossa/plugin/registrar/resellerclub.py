from datetime import datetime

from fossa.plugin.registrar import Registrar


def _epoch(timestamp):
    return datetime.fromtimestamp(int(timestamp))


class ResellerClub(Registrar):
    RECORD_LIMIT = 100
    def __init__(self, user_id, api_key, url="https://httpapi.com/", **kwargs):
        self.url = url
        self.user_id = user_id
        self.name = str(user_id)
        self.api_key = api_key
        super().__init__(**kwargs)

    def __request(self, uri, data={}):
        data['auth-userid'] = self.user_id
        data['api-key'] = self.api_key
        return self.session.get(self.url + uri, params=data)

    def __post_request(self, uri, data={}):
        data['auth-userid'] = self.user_id
        data['api-key'] = self.api_key
        return self.session.post(self.url + uri, params=data)

    def list(self):
        page = 1
        while True:
            response = self.__request('api/domains/search.json',
                                      {'no-of-records': self.RECORD_LIMIT,
                                       'page-no': page})

            records = response.json()
            if response.status_code != 200:
                self.error(records['message'])
                return

            count = int(records['recsonpage'])

            for index in range(1, count + 1):
                entry = records[str(index)]
                yield {
                    'id': entry['entity.entityid'],
                    'domain': entry['entity.description'],
                    'expire': _epoch(entry['orders.endtime']) if 'orders.endtime' in entry else None,
                    'privacy': entry['orders.privacyprotection'] == 'true' if 'orders.privacyprotection' in entry else False,
                    'transferAllowed': not entry['orders.transferlock'],
                    'autoRenew': entry['orders.autorenew'] == 'true',
                    'registrar': self
                }
            if count < self.RECORD_LIMIT:
                break
            page += 1
