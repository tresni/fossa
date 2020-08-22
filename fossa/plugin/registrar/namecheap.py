from datetime import datetime
from math import ceil
from xml.etree import ElementTree

from fossa.plugin.registrar import Registrar
from dateutil.parser import parse


def _epoch(timestamp):
    return datetime.fromtimestamp(int(timestamp))


class Namecheap(Registrar):
    RECORD_LIMIT = 100

    def __init__(self, username, api_key, api_user=None, client_ip="0.0.0.0", url="https://api.namecheap.com/xml.response", **kwargs):
        self.url = url
        self.username = username
        self.api_user = api_user if api_user else username
        self.name = "{}/{}".format(api_user, username) if api_user else str(username)
        self.api_key = api_key
        self.client_ip = client_ip
        super().__init__(**kwargs)

    def _required_data(self, command, extend={}):
        data = {
            "ApiUser": self.api_user,
            "ApiKey": self.api_key,
            "UserName": self.username,
            "ClientIp": self.client_ip,
            "Command": command
        }
        data.update(extend)
        return data

    def list(self):
        page = 1
        totalPages = 1 # Lies, but...
        while page <= totalPages:
            response = self.session.post(self.url,
                                         self._required_data("namecheap.domains.getList",
                                                             {"PageSize": self.RECORD_LIMIT,
                                                              "Page": page}))

            tree = ElementTree.fromstring(response.content)
            if tree.attrib['Status'].upper() == 'ERROR':
                errors = tree.find('./{http://api.namecheap.com/xml.response}Errors')
                self.error("The following errors were encountered:")
                for error in errors:
                    self.error("\t%s" % error.text)
                break
            cr = tree.find(".//{http://api.namecheap.com/xml.response}CommandResponse")

            if totalPages == 1:
                total = cr.find("./{0}Paging/{0}TotalItems".format("{http://api.namecheap.com/xml.response}"))
                totalPages = ceil(int(total.text) / self.RECORD_LIMIT)

            tree = ElementTree.fromstring(response.content)
            results = cr.find("./{http://api.namecheap.com/xml.response}DomainGetListResult")
            for domain in results:
                yield {
                    'id': domain.attrib['ID'],
                    'domain': domain.attrib['Name'],
                    'expire': parse(domain.attrib['Expires']),
                    'privacy': domain.attrib['WhoisGuard'] == 'ENABLED',
                    'transferAllowed': domain.attrib['IsLocked'],
                    'autoRenew': domain.attrib['AutoRenew'],
                    'registrar': self
                }
            page += 1
