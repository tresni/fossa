import hashlib
from base64 import b64encode

from fossa.plugin.registrar import Registrar

from dateutil.parser import parse

# https://devblog.easyname.com/rest/domain/


def b64md5(data):
    return b64encode(hashlib.md5(data).hexdigest().encode("utf-8")).decode('utf-8')


class Easyname(Registrar):
    def __init__(self, user_id, email, api_key, authentication_salt, signing_salt, **kwargs):
        self.name = "{}/{}".format(email, user_id)
        to_sign = (authentication_salt % (user_id, email)).encode("utf-8")
        self.signing_salt = signing_salt
        super().__init__(**kwargs)
        self.session.headers.update({
            "X-User-ApiKey": api_key,
            "X-User-Authentication": b64md5(to_sign)
        })

    def __sign(self, data):
        pass

    def list(self):
        response = self.session.get("https://api.easyname.com/domain")
        if response.status_code != 200:
            self.error("Something failed")
            return
        for x in response.json()["data"]:
            x.update({"registrar": self, "expire": parse(x["expire"])})
            yield x
