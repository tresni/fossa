from datetime import datetime

from fossa.plugin.registrar import Registrar


def _epoch(timestamp):
    return datetime.fromtimestamp(int(timestamp))


class ResellerClub(Registrar):
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
        page = 0
        limit = 100
        while True:
            response = self.__request('api/domains/search.json', {'no-of-records': limit,
                                                                  'page-no': page})
            temp_list = response.json()
            if response.status_code != 200:
                self.error(temp_list['message'])
                return

            for index in range(1, int(temp_list['recsonpage']) + 1):
                entry = temp_list[str(index)]
                yield {
                    'id': entry['entity.entityid'],
                    'domain': entry['entity.description'],
                    'expire': _epoch(entry['orders.endtime']) if 'orders.endtime' in entry else None,
                    'privacy': entry['orders.privacyprotection'] == 'true' if 'orders.privacyprotection' in entry else False,
                    'transferAllowed': not entry['orders.transferlock'],
                    'autoRenew': entry['orders.autorenew'] == 'true',
                    'registrar': self
                }
            page += 1
            if page * limit >= int(temp_list['recsindb']):
                break
