from __future__ import annotations

import logging
import os
import shlex
import warnings
from typing import Optional

os.environ.setdefault("TERM", "xterm-256color")
warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger("prompt_toolkit").setLevel(logging.ERROR)

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mailai import contacts, history
from mailai.config import config
from mailai.engine import EngineResult, process_chat
from typing import Any, Dict, List
from mailai.imap_client import list_inbox, list_sent, read_email

console = Console()

PENDING: Optional[EngineResult] = None
CHAT_HISTORY: List[Dict[str, Any]] = []


def cmd_help() -> None:
    console.print(Panel.fit(
        "[bold]MailAI[/bold] - Envoie des emails en langage naturel\n\n"
        "Commandes disponibles :\n"
        "  [cyan]/send[/cyan] ou [cyan]/confirm[/cyan]   Envoyer l'email préparé\n"
        "  [cyan]/cancel[/cyan]               Annuler l'email en cours\n"
        "  [cyan]/contacts[/cyan]             Lister les contacts\n"
        "  [cyan]/add <nom> <email>[/cyan]    Ajouter un contact\n"
        "  [cyan]/del <id>[/cyan]             Supprimer un contact\n"
        "  [cyan]/search <q>[/cyan]           Chercher un contact\n"
        "  [cyan]/history[/cyan]              Voir l'historique\n"
        "  [cyan]/inbox[/cyan]                Voir les derniers emails reçus\n"
        "  [cyan]/read <n>[/cyan]              Lire un email reçu (numero dans /inbox)\n"
        "  [cyan]/sent[/cyan]                  Voir les emails envoyés\n"
        "  [cyan]/config[/cyan]               Voir la configuration\n"
        "  [cyan]/help[/cyan]                 Cette aide\n"
        "  [cyan]/quit[/cyan]                 Quitter\n\n"
        "Sinon, tape directement une instruction en langage naturel.\n"
        "  Ex: [italic]\"envoie un email à Jean pour la réunion de demain\"[/italic]",
        title="📬 MailAI",
    ))


def cmd_contacts_list() -> None:
    all_contacts = contacts.list_all()
    if not all_contacts:
        console.print("[yellow]Aucun contact. Ajoutes-en avec /add <nom> <email>[/yellow]")
        return
    table = Table(title="Carnet d'adresses")
    table.add_column("ID", style="dim")
    table.add_column("Nom")
    table.add_column("Email")
    for c in all_contacts:
        table.add_row(str(c.id), c.name, c.email)
    console.print(table)


def cmd_contacts_add(args: list[str]) -> None:
    if len(args) < 2:
        console.print("[red]Usage : /add <nom> <email>[/red]")
        return
    name = args[0]
    email = args[1]
    existing = contacts.find_by_name(name)
    if existing:
        console.print(f"[yellow]Le contact « {name} » existe déjà ({existing.email}).[/yellow]")
        return
    contact = contacts.add(name, email)
    console.print(f"[green]Contact ajouté : {contact}[/green]")


def cmd_contacts_del(args: list[str]) -> None:
    if not args:
        console.print("[red]Usage : /del <id>[/red]")
        return
    try:
        contact_id = int(args[0])
    except ValueError:
        console.print("[red]L'ID doit être un nombre.[/red]")
        return
    if contacts.delete(contact_id):
        console.print(f"[green]Contact #{contact_id} supprimé.[/green]")
    else:
        console.print("[red]Contact introuvable.[/red]")


def cmd_search(args: list[str]) -> None:
    if not args:
        console.print("[red]Usage : /search <query>[/red]")
        return
    query = " ".join(args)
    results = contacts.search(query)
    if not results:
        console.print("[yellow]Aucun résultat.[/yellow]")
        return
    table = Table(title=f"Résultats pour « {query} »")
    table.add_column("ID", style="dim")
    table.add_column("Nom")
    table.add_column("Email")
    for c in results:
        table.add_row(str(c.id), c.name, c.email)
    console.print(table)


def cmd_history() -> None:
    entries = history.list_recent(limit=15)
    if not entries:
        console.print("[yellow]Aucun historique.[/yellow]")
        return
    table = Table(title="Historique des envois")
    table.add_column("Date")
    table.add_column("Statut")
    table.add_column("Destinataire")
    table.add_column("Sujet")
    for e in entries:
        status_style = "green" if e.status == "sent" else "red"
        console.print()
        console.print(f"[{status_style}]{e.status.upper()}[/{status_style}] {e.created_at}")
        console.print(f"  À: {e.to_name or e.to_email}")
        console.print(f"  Sujet: {e.subject}")
        if e.error:
            console.print(f"  [red]Erreur: {e.error}[/red]")
    console.print()


def cmd_config() -> None:
    valid, errors = config.is_valid
    console.print(Panel.fit(
        f"[bold]OpenAI[/bold]\n"
        f"  Modèle : {config.openai_model}\n"
        f"  Clé API : {'✓ définie' if config.openai_api_key else '✗ manquante'}\n\n"
        f"[bold]SMTP OVH[/bold]\n"
        f"  Serveur : {config.smtp_server}:{config.smtp_port}\n"
        f"  Utilisateur : {config.smtp_username or '✗ manquant'}\n"
        f"  Mot de passe : {'✓ défini' if config.smtp_password else '✗ manquant'}\n"
        f"  Email expéditeur : {config.smtp_from_email or '✗ manquant'}\n\n"
        f"[bold]Base de données[/bold]\n"
        f"  Chemin : {config.db_path}\n\n"
        f"[bold]Configuration : {'✓ valide' if valid else '✗ incomplète'}[/bold]",
        title="Configuration",
    ))
    if not valid:
        for err in errors:
            console.print(f"  [red]• {err}[/red]")




def cmd_inbox() -> None:
    try:
        emails = list_inbox(limit=10)
        if not emails:
            console.print("[yellow]Boîte de réception vide.[/yellow]")
            return
        table = Table(title="Boîte de réception")
        table.add_column("#", style="dim")
        table.add_column("Date")
        table.add_column("Expéditeur")
        table.add_column("Sujet")
        for i, e in enumerate(emails, 1):
            table.add_row(str(i), e.date[:16], e.sender[:30], e.subject[:40])
        console.print(table)
        console.print("Tape [cyan]/read <n>[/cyan] pour lire un email.")
    except Exception as ex:
        console.print(f"[red]Erreur IMAP : {ex}[/red]")


def cmd_read(args: list[str]) -> None:
    if not args:
        console.print("[red]Usage : /read <numero>[/red]")
        return
    try:
        n = int(args[0])
    except ValueError:
        console.print("[red]Le numéro doit être un nombre.[/red]")
        return
    try:
        emails = list_inbox(limit=10)
        if n < 1 or n > len(emails):
            console.print(f"[red]Numéro invalide (1-{len(emails)}).[/red]")
            return
        full = read_email(emails[n - 1].uid)
        if not full:
            console.print("[red]Impossible de lire cet email.[/red]")
            return
        console.print(Panel.fit(
            f"[bold]De:[/bold] {full.sender}\n"
            f"[bold]Date:[/bold] {full.date}\n"
            f"[bold]Sujet:[/bold] {full.subject}\n\n"
            f"{full.body_text[:2000]}",
            title=f"Email #{n}"
        ))
    except Exception as ex:
        console.print(f"[red]Erreur IMAP : {ex}[/red]")


def cmd_sent() -> None:
    try:
        emails = list_sent(limit=10)
        if not emails:
            console.print("[yellow]Aucun email envoyé trouvé.[/yellow]")
            return
        table = Table(title="Emails envoyés")
        table.add_column("#", style="dim")
        table.add_column("Date")
        table.add_column("Destinataire")
        table.add_column("Sujet")
        for i, e in enumerate(emails, 1):
            table.add_row(str(i), e.date[:16], e.recipient[:30], e.subject[:40])
        console.print(table)
    except Exception as ex:
        console.print(f"[red]Erreur IMAP : {ex}[/red]")


def show_pending() -> None:
    if PENDING is None:
        return
    console.print(Panel.fit(
        f"[bold]À:[/bold] {PENDING.to_name} <{PENDING.to_email}>\n"
        f"[bold]Sujet:[/bold] {PENDING.subject}\n"
        f"[bold]Corps:[/bold]\n{PENDING.body}",
        title="Email préparé"
    ))
    console.print("Tape [cyan]/send[/cyan] pour envoyer, [cyan]/cancel[/cyan] pour annuler, ou modifie l'instruction.")


def handle_command(cmd: str, args: list[str]) -> bool:
    global PENDING

    if cmd == "quit":
        return False
    elif cmd == "help":
        cmd_help()
    elif cmd == "send" or cmd == "confirm":
        if PENDING is None:
            console.print("[yellow]Rien à envoyer. Donne d'abord une instruction.[/yellow]")
            return True
        from mailai.engine import confirm_and_send
        result = confirm_and_send(PENDING.to_name, PENDING.to_email, PENDING.subject, PENDING.body)
        if result.success:
            console.print(f"[green]{result.message}[/green]")
        else:
            console.print(f"[red]{result.message}[/red]")
        PENDING = None
    elif cmd == "cancel":
        if PENDING:
            console.print("[yellow]Email annulé.[/yellow]")
        PENDING = None
    elif cmd == "contacts":
        cmd_contacts_list()
    elif cmd == "add":
        cmd_contacts_add(args)
    elif cmd == "del" or cmd == "delete":
        cmd_contacts_del(args)
    elif cmd == "search" or cmd == "find":
        cmd_search(args)
    elif cmd == "history":
        cmd_history()
    elif cmd == "config":
        cmd_config()
    elif cmd == "inbox":
        cmd_inbox()
    elif cmd == "read":
        cmd_read(args)
    elif cmd == "sent":
        cmd_sent()
    else:
        console.print(f"[red]Commande inconnue : /{cmd}[/red]")
    return True


def run() -> None:
    global PENDING

    console.print("[bold blue]MailAI[/bold blue] - Assistant email en langage naturel")
    console.print("Tape [cyan]/help[/cyan] pour voir les commandes disponibles, [cyan]/quit[/cyan] pour quitter.\n")

    from pathlib import Path
    history_path = str(Path("~/.mailai_history").expanduser())
    session = PromptSession(history=FileHistory(history_path))

    while True:
        try:
            text = session.prompt("📬 ")
        except (EOFError, KeyboardInterrupt):
            console.print("\nAu revoir !")
            break

        text = text.strip()
        if not text:
            continue

        if text.startswith("/"):
            parts = shlex.split(text[1:])
            cmd = parts[0].lower() if parts else ""
            cmd_args = parts[1:] if len(parts) > 1 else []
            if not handle_command(cmd, cmd_args):
                break
        else:
            CHAT_HISTORY.append({"role": "user", "content": text})
            with console.status("[bold green]L'IA réfléchit..."):
                result = process_chat(CHAT_HISTORY)
            
            if result.text:
                console.print(Panel.fit(result.text, title="MailAI", border_style="blue"))
                
            if result.pending_email:
                PENDING = result.pending_email
                show_pending()
