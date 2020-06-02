import os
from datetime import datetime, timedelta

from fossa import APP_NAME

import click
import toml
from stevedore import extension

registrar_plugins = extension.ExtensionManager(
    namespace="fossa.plugin.registrar",
    invoke_on_load=False,
    on_load_failure_callback=print
)

configured_registrars = []

with open(os.path.join(click.get_app_dir(APP_NAME), 'config.toml')) as fp:
    opts = toml.load(fp)
    for name in opts["registrar"]:
        if name in registrar_plugins:
            for conf in opts["registrar"][name]:
                configured_registrars.append(registrar_plugins[name].plugin(**conf))
        else:
            click.echo("{} is not a registrar plugin".format(name))


@click.group()
def cli():
    pass


@cli.group()
def domain():
    pass


@domain.command()
@click.option("-e", "--expires-in", "expires_in", type=click.INT)
def list(expires_in):
    domains = []
    for r in configured_registrars:
        [domains.append(domain) for domain in r.list()]

    max_domain = max(domains, key=lambda k: len(k["domain"]))
    domain_length = len(max_domain["domain"])
    domains = sorted(domains, key=lambda k: k["expire"])
    if expires_in:
        domains = filter(lambda k: k["expire"] - datetime.now() < timedelta(days=expires_in), domains)
    for v in domains:
        print("{name:{width}} {expires} {registrar!s}".format(
            name=v["domain"],
            expires=v["expire"],
            registrar=v["registrar"],
            width=domain_length))


@cli.command()
def plugins():
    for name, _ in registrar_plugins.items():
        print(name)


@cli.command()
def registrars():
    print("\n".join(map(str, configured_registrars)))


if __name__ == "__main__":
    cli()
