from __future__ import annotations

import sys

import click

from mailai import contacts
from mailai import history as history_db
from mailai.config import config
from mailai.db import close as db_close
from mailai.engine import process
from mailai.repl import run as run_repl


@click.group()
@click.option("--env-file", default=None, help="Chemin vers le fichier .env")
def cli(env_file: str | None) -> None:
    """MailAI - Envoie des emails en langage naturel via OpenAI + OVH."""
    config.load(env_file)


@cli.command()
@click.argument("message", required=False)
@click.option("--yes", "-y", is_flag=True, help="Envoyer sans confirmation")
def send(message: str | None, yes: bool) -> None:
    """Analyser et envoyer un email en langage naturel."""
    if not message:
        if sys.stdin.isatty():
            click.echo("Usage: mailai send <message>")
            raise SystemExit(1)
        message = sys.stdin.read().strip()

    if not message:
        click.echo("Message vide.", err=True)
        raise SystemExit(1)

    result = process(message, auto_confirm=yes)
    if result.success and result.body:
        if not yes:
            click.echo()
            click.echo("─" * 50)
            click.echo(f"  À:      {result.to_name} <{result.to_email}>")
            click.echo(f"  Sujet:  {result.subject}")
            click.echo(f"  Corps:")
            for line in result.body.split("\n"):
                click.echo(f"    {line}")
            click.echo("─" * 50)
            click.echo()
            click.confirm("Envoyer cet email ?", abort=True)
            from mailai.engine import confirm_and_send
            result = confirm_and_send(
                result.to_name, result.to_email, result.subject, result.body
            )

        if result.success:
            click.echo(f"✓ {result.message}")
        else:
            click.echo(f"✗ {result.message}", err=True)
            raise SystemExit(1)
    else:
        click.echo(f"✗ {result.message}", err=True)
        raise SystemExit(1)


@cli.command()
def repl() -> None:
    """Mode interactif (REPL)."""
    valid, errors = config.is_valid
    if not valid:
        for err in errors:
            click.echo(f"✗ {err}", err=True)
        if errors:
            click.echo("Configure le fichier .env et réessaie.", err=True)
            raise SystemExit(1)
    try:
        run_repl()
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        db_close()


@cli.group()
def contacts_group() -> None:
    """Gérer le carnet d'adresses."""
    pass


@contacts_group.command("list")
def contacts_list() -> None:
    """Lister tous les contacts."""
    all_contacts = contacts.list_all()
    if not all_contacts:
        click.echo("Aucun contact.")
        return
    for c in all_contacts:
        click.echo(f"  {c.id:>3}  {c.name:<20} {c.email}")


@contacts_group.command("add")
@click.argument("name")
@click.argument("email")
def contacts_add(name: str, email: str) -> None:
    """Ajouter un contact."""
    existing = contacts.find_by_name(name)
    if existing:
        click.echo(f"Le contact « {name} » existe déjà ({existing.email}).")
        raise SystemExit(1)
    c = contacts.add(name, email)
    click.echo(f"Contact ajouté : {c}")


@contacts_group.command("delete")
@click.argument("contact_id", type=int)
def contacts_delete(contact_id: int) -> None:
    """Supprimer un contact."""
    if contacts.delete(contact_id):
        click.echo(f"Contact #{contact_id} supprimé.")
    else:
        click.echo("Contact introuvable.", err=True)
        raise SystemExit(1)


@contacts_group.command("search")
@click.argument("query")
def contacts_search(query: str) -> None:
    """Chercher un contact."""
    results = contacts.search(query)
    if not results:
        click.echo("Aucun résultat.")
        return
    for c in results:
        click.echo(f"  {c.id:>3}  {c.name:<20} {c.email}")


@cli.command()
def history() -> None:
    """Voir l'historique des envois."""
    entries = history_db.list_recent()
    if not entries:
        click.echo("Aucun historique.")
        return
    for e in entries:
        status = "✓" if e.status == "sent" else "✗"
        click.echo(f"  [{status}] {e.created_at}  → {e.to_name or e.to_email}  |  {e.subject}")
        if e.error:
            click.echo(f"       Erreur: {e.error}")
