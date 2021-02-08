from datetime import datetime

from fossa.plugin.registrar import Registrar
from bs4 import BeautifulSoup


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
#                yield {
#                    'id': entry['entity.entityid'],
#                    'domain': entry['entity.description'],
#                    'expire': _epoch(entry['orders.endtime']) if 'orders.endtime' in entry else None,
#                    'privacy': entry['orders.privacyprotection'] == 'true' if 'orders.privacyprotection' in entry else False,
#                    'transferAllowed': not entry['orders.transferlock'],
#                    'autoRenew': entry['orders.autorenew'] == 'true',
#                    'registrar': self
#                }
            if count < self.RECORD_LIMIT:
                break
            page += 1


class FoundationAPI(Registrar):
    RECORD_LIMIT = 100
    def __init__(self, username, password, reseller, url="https://foundationapi.com/", role="customer", **kwargs):
        self.url = url
        self.username = username
        self.name = str(username)
        self.password = password
        self.reseller = reseller
        self.role = role
        super().__init__(**kwargs)

    def __request(self, uri, data={}):
        return self.session.get(self.url + uri, params=data)

    def __post_request(self, uri, data={}):
        return self.session.post(self.url + uri, params=data)

    def login(self):
        response = self.__post_request('servlet/AuthServlet', {
            "pid": self.reseller,
            "username": self.username,
            "password": self.password,
            "role": self.role
        })
        self.password = None
        if not response.history:
            return False

        return True

    def _is_private(self):
        # https://cp.midominio.do/servlet/PrivacyProtectionServlet?validatenow=false&orderid=76286191&domainname=vpn.do&productcategory=domorder&_=1612817310888
        pass

    def _is_locked(self):
        # https://cp.midominio.do/servlet/TheftProtectionServlet?validatenow=false&orderid=76286191&domainname=vpn.do&productcategory=domorder&_=1612817310889
        pass

    def list(self):
        if not self.login():
            self.error("Invalid login")
            return

        page = 1
        while True:
            response = self.__request('servlet/ListAllOrdersServlet',
                {
                    "formaction": "onlyOrdersList",
                    "pageno": page,
                    "forproduct": "domain_registration_group",
                    "searchfor": "domain",
                    "show_only_expiring_orders": "false",
                    "ppExpiry": "any",
                    "recperpage": self.RECORD_LIMIT
                })

            if response.status_code != 200:
                self.error(response.status_code)
                return

            try:
                soup = BeautifulSoup(response.text, "lxml")
            except Exception:
                soup = BeautifulSoup(response.text, "html.parser")
            domains = soup.find_all("tr")
            count = len(domains)
            for d in domains[1:]:
                domainid = d.find('input', {"name": "orderid"})['value']
                yield {
                    "id": domainid,
                    "domain": d.find('input', {"name": "%s_domain_name" % domainid})['value'],
                    "expire": _epoch(d.find('input', {"name": "%s_expirydate" % domainid})['value']),
                    "privacy": False, #self._is_private()
                    "transferAllowed": False, #self._is_locked()
                    "autoRenew": False, #self._auto_renew()
                    "registrar": self,
                }

            if count < self.RECORD_LIMIT:
                break
            page += 1
