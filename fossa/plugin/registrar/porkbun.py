from http.cookies import SimpleCookie

from fossa.plugin.registrar import Registrar

from bs4 import BeautifulSoup
from dateutil.parser import parse
from requests.utils import cookiejar_from_dict

# https://porkbun.com/api/domains/getDomainManagementDetailsSlow?domain=hartvigsen.xyz
# https://porkbun.com/api/domains/getDomainManagementDetails?domain=hartvigsen.xyz
# $.post("/api/domains/getAuthCode", {domain:domain, domainPassword: password, twoFactor: twoFactor},
# $.post("/api/domains/passwordProtectDomain", {domain: domain, domainPassword: password, twoFactor: twoFactor},
# $.post("/api/domains/lockUnlock", {domain: domain},
# $.post("/api/domains/disableWhoisProtection", {domain: domain},
# $.post("/api/domains/enableWhoisProtection", {domain: domain, type: ("private"|"redacted")},
# $.post("/api/domains/approvePendingTransfer", {domain:domain, op:op},

# $.post("/api/user/getAccountCsvFile", {empty:true},

# These are Toggles!
# $.post("/api/domains/enableDisableWhoisProtection", {domain: domain},
# $.post("/api/domains/enableDisableAutoRenew", {domain: domain},


class Porkbun(Registrar):
    def __init__(self, cookie, **kwargs):
        C = SimpleCookie()
        C.load(cookie)
        self.name = C['BUNSOURCE'].value

        cookies = {}
        [cookies.update({k: C[k].value}) for k in C]

        super().__init__(**kwargs)
        self.session.cookies = cookiejar_from_dict(cookies)
        if 'user-agent' in kwargs:
            self.session.headers.update({"user-agent": kwargs['user-agent']})

    def list(self):
        response = self.session.get('https://porkbun.com/account/domains', allow_redirects=False)
        if response.status_code != 200:
            self.error("Invalid login information, update cookie & user-agent")
            return
        try:
            soup = BeautifulSoup(response.text, "lxml")
        except Exception:
            soup = BeautifulSoup(response.text, "html.parser")
        domains = soup.find_all("div", class_="domainManagementRow")
        for d in domains:
            yield {
                "domain": d["data-domain"],
                "expire": parse(d["data-expiration"]),
                "privacy": True if d["data-privacy"] == "1" else False,
                "transferAllowed": False if d["data-lock"] == "1" else True,
                "autoRenew": True if d["data-autorenew"] == "1" else False,
                "registrar": self
                # data-ssl="0" data-email="0" data-website="0">
            }
