# Fossa

A domain management tool

## Description

This tool is designed to make managing domains with multiple registrars easier.
As such, it leverages official APIs whenever possible, but will resort to scraping if no official API is found or known.

## Configuration

Configuration is done in a TOML file named `config.toml`.  This is stored in the [`get_app_dir`](https://click.palletsprojects.com/en/7.x/api/#click.get_app_dir) under a folder named `fossa`.  Each registrar has their own configuration requirements, see below.  Multiple instances of the same registrar with different credentials can be utilized.

To cache requests add `cache = [seconds]` to the configuration blocks described below.  By default, there is no caching except as noted for specific registrars.  Caching is done at a per registrar instance level.

`[[registrar.*]]` blocks can be given a custom name by adding `name = "NAME"` to the configuration block.  Names are otherwise determined by the registrar plugin to allow for differentiation of multiple instances.

## Supported Registrars

### Porkbun

```toml
[[registrar.porkbun]]
cookie = "See below"
user-agent = "See below"
```

Porkbun does not have an official API that can be used at this time. Sign-in to Porkbun and [grab your Cookies](https://github.com/Jackett/Jackett/wiki/Finding-cookies).  Also, capture your [`User-Agent`](https://duckduckgo.com/?q=what+is+my+user+agent&ia=answer) string.  This must match exactly or the cookie data will not validate.

### easyname

```toml
[[registrar.easyname]]
user_id = 123
email = "support@easyname.eu"
api_key = "abcd1234"
authentication_salt = "Signing%sTopSecret%sAuth00"
signing_salt = "SuperSecretSigningSalt"
```

API access and credentials can be found under [Account > API-Access](https://my.easyname.com/en/account/api). Copy the credential information as displayed on that page into the appropriate fields.

The easyname API documentation can be found at https://devblog.easyname.com/api/ .

### internet.bs

```toml
[[registrar.internetbs]]
api_key = "API KEY"
password = "ACCOUNT PASSWORD"
```

To get API access login to your account, under the menu 'My Account' and click on 'Get my API key'.  You must have a positive balance in your account to request an API key.  Due to unpublished API limits, a 10-minute cache is used by default for all Internet.bs requests.

If you would like to use the test server, use the following configuration block:

```toml
[[registrar.internetbs]]
api_key = "testapi"
password = "testpass"
url = "https://testapi.internet.bs"
```

The internet.bs API documentation can be found at https://internetbs.net/internet-bs-api.pdf .

### ResellerClub

```toml
[[registrar.resellerclub]]
user_id = 123456789
api_key = "API KEY"
```

To get your User Id (also called Reseller Id), click the profile icon in the top right corner.  Your API Key can be found under Settings > API.

If you would like to use the test server, just add `url = "https://test.httpapi.com/"` to the configuration block.

The ResellerClub API documentation can be found at  https://resellerclub.webpropanel.com/kb/answer/744 .


### Gandi

```toml
[[registrar.gandi]]
api_key = "API KEY"
```

Gandi API documentation can be found at https://api.gandi.net/docs/domains/ .

### Adding new registrars

Adding support for new registrars is as easy as writing a plugin that inherits from the [Registrar](fossa/plugin/registrar/__init__.py) class, and then specifying the appropriate `fossa.plugin.registrar` entrypoint in the projects setup.py.  Of course, pull requests to add registrars are also welcome.
