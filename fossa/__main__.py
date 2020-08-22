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
max_registrar = 0

with open(os.path.join(click.get_app_dir(APP_NAME), 'config.toml')) as fp:
    opts = toml.load(fp)
    for name in opts["registrar"]:
        if name in registrar_plugins:
            for conf in opts["registrar"][name]:
                if len(registrar_plugins[name].plugin.__name__) > max_registrar:
                    max_registrar = len(registrar_plugins[name].plugin.__name__)
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
@click.option("-r", "--registrar", multiple=True)
def list(expires_in, registrar):
    domains = []
    for r in configured_registrars:
        if (registrar and str(r) in registrar) or not registrar:
            [domains.append(domain) for domain in r.list()]

    if not domains:
        return
    max_domain = max(domains, key=lambda k: len(k["domain"]))
    domain_length = len(max_domain["domain"])
    domains = sorted(domains, key=lambda k: k["expire"])
    if expires_in:
        domains = filter(lambda k: k["expire"] - datetime.now() < timedelta(days=expires_in), domains)
    for v in domains:
        print("{name:{width}} {expires} {registrar:{max_registrar}} {account}".format(
            name=v["domain"],
            expires=v["expire"],
            registrar=v["registrar"].__class__.__name__,
            max_registrar=max_registrar,
            account=v["registrar"].name,
            width=domain_length))


@cli.command()
def plugins():
    for name, v in registrar_plugins.items():
        print("{} (registrar.{})".format(v.plugin.__name__, name))


@cli.command()
def registrars():
    c = sorted(configured_registrars, key=lambda k: k.__class__.__name__)
    class_ = None
    for registrar in c:
        if registrar.__class__.__name__ != class_:
            class_ = registrar.__class__.__name__
            click.echo(class_)
        click.echo("* {}".format(registrar.name))


if __name__ == "__main__":
    cli()
