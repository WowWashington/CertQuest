"""
Community topic downloader for CertQuest.

Downloads certification packs from the CertQuest-Topics GitHub repository
and installs them into the local certifications/ directory.

Uses only Python stdlib (urllib) — no additional dependencies required.
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Repository configuration
TOPICS_REPO = "WowWashington/CertQuest-Topics"
TOPICS_BRANCH = "main"
TOPICS_INDEX_URL = (
    f"https://raw.githubusercontent.com/{TOPICS_REPO}/{TOPICS_BRANCH}/topics.json"
)
RAW_BASE_URL = (
    f"https://raw.githubusercontent.com/{TOPICS_REPO}/{TOPICS_BRANCH}"
)

# Optional colorama support (matches display.py pattern)
try:
    from colorama import Fore, Style
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

    class Fore:
        RED = ""
        GREEN = ""
        YELLOW = ""
        CYAN = ""
        MAGENTA = ""
        WHITE = ""
        RESET = ""

    class Style:
        BRIGHT = ""
        DIM = ""
        RESET_ALL = ""


def _get_certifications_dir():
    """Get the path to the certifications directory."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "certifications")


def _get_installed_topics():
    """Return set of certification IDs already installed locally."""
    certs_dir = _get_certifications_dir()
    installed = set()
    if os.path.isdir(certs_dir):
        for name in os.listdir(certs_dir):
            config_path = os.path.join(certs_dir, name, "config.yaml")
            if os.path.isfile(config_path):
                installed.add(name)
    return installed


def _fetch_url(url, description="content"):
    """Fetch content from a URL. Returns bytes or None on failure."""
    try:
        req = Request(url, headers={"User-Agent": "CertQuest-Downloader/1.0"})
        with urlopen(req, timeout=15) as response:
            return response.read()
    except HTTPError as e:
        print(f"\n    {Fore.RED}Error downloading {description}: HTTP {e.code}{Style.RESET_ALL}")
        return None
    except URLError as e:
        print(f"\n    {Fore.RED}Network error: {e.reason}{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"\n    {Fore.RED}Error: {e}{Style.RESET_ALL}")
        return None


def _fetch_topics_index():
    """Fetch and parse the topics.json index from GitHub."""
    print("\n    Fetching available topics...")
    data = _fetch_url(TOPICS_INDEX_URL, "topics index")
    if data is None:
        return None
    try:
        index = json.loads(data.decode("utf-8"))
        return index
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"\n    {Fore.RED}Error parsing topics index: {e}{Style.RESET_ALL}")
        return None


def _display_topics(topics, installed):
    """Display available topics with install status."""
    print("\n    ╔══════════════════════════════════════════════════════════════════╗")
    print("    ║                  Community Topics                               ║")
    print("    ╚══════════════════════════════════════════════════════════════════╝\n")

    if not topics:
        print("    No community topics available yet.\n")
        return

    for i, topic in enumerate(topics, 1):
        topic_id = topic.get("id", "unknown")
        name = topic.get("name", topic_id)
        full_name = topic.get("full_name", "")
        org = topic.get("organization", "")
        domains = topic.get("domain_count", 0)
        scenarios = topic.get("scenario_count", 0)
        description = topic.get("description", "")

        is_installed = topic_id in installed

        if is_installed:
            status = f"{Fore.GREEN}[INSTALLED]{Style.RESET_ALL}" if HAS_COLOR else "[INSTALLED]"
        else:
            status = f"{Fore.YELLOW}[AVAILABLE]{Style.RESET_ALL}" if HAS_COLOR else "[AVAILABLE]"

        if HAS_COLOR:
            num = f"{Fore.CYAN}[{i}]{Style.RESET_ALL}"
        else:
            num = f"[{i}]"

        print(f"    {num} {name}  {status}")
        if full_name:
            print(f"        {full_name}")
        if org:
            print(f"        Organization: {org}")
        print(f"        Domains: {domains}  |  Scenarios: {scenarios}")
        if description:
            print(f"        {Style.DIM}{description}{Style.RESET_ALL}")
        print()

    print(f"    [B] Back to main menu\n")


def _download_topic(topic):
    """Download and install a single topic. Returns True on success."""
    topic_id = topic.get("id", "unknown")
    name = topic.get("name", topic_id)
    files = topic.get("files", [])

    if not files:
        print(f"\n    {Fore.RED}Error: Topic '{name}' has no files listed.{Style.RESET_ALL}")
        return False

    certs_dir = _get_certifications_dir()
    topic_dir = os.path.join(certs_dir, topic_id)

    print(f"\n    Downloading {name}...")
    print(f"    Installing to: certifications/{topic_id}/\n")

    success_count = 0
    fail_count = 0

    for file_path in files:
        url = f"{RAW_BASE_URL}/{topic_id}/{file_path}"
        local_path = os.path.join(topic_dir, file_path)

        # Create subdirectories as needed
        local_dir = os.path.dirname(local_path)
        os.makedirs(local_dir, exist_ok=True)

        # Show progress
        if HAS_COLOR:
            print(f"    {Fore.CYAN}↓{Style.RESET_ALL} {file_path}...", end=" ", flush=True)
        else:
            print(f"    ↓ {file_path}...", end=" ", flush=True)

        data = _fetch_url(url, file_path)
        if data is not None:
            try:
                with open(local_path, "wb") as f:
                    f.write(data)
                if HAS_COLOR:
                    print(f"{Fore.GREEN}OK{Style.RESET_ALL}")
                else:
                    print("OK")
                success_count += 1
            except IOError as e:
                if HAS_COLOR:
                    print(f"{Fore.RED}FAILED ({e}){Style.RESET_ALL}")
                else:
                    print(f"FAILED ({e})")
                fail_count += 1
        else:
            fail_count += 1

    # Validate installation
    config_path = os.path.join(topic_dir, "config.yaml")
    if not os.path.isfile(config_path):
        print(f"\n    {Fore.RED}Warning: config.yaml not found — installation may be incomplete.{Style.RESET_ALL}")
        return False

    # Summary
    print(f"\n    {'─' * 50}")
    if fail_count == 0:
        if HAS_COLOR:
            print(f"    {Fore.GREEN}✓ Successfully installed '{name}'!{Style.RESET_ALL}")
        else:
            print(f"    ✓ Successfully installed '{name}'!")
        print(f"    {success_count} files downloaded.")
        print(f"\n    Return to the main menu to play it.")
    else:
        if HAS_COLOR:
            print(f"    {Fore.YELLOW}⚠ Partially installed '{name}'.{Style.RESET_ALL}")
        else:
            print(f"    ⚠ Partially installed '{name}'.")
        print(f"    {success_count} succeeded, {fail_count} failed.")
        print(f"    Try downloading again to retry failed files.")

    return fail_count == 0


def run_topic_browser():
    """
    Main entry point for the community topic browser.

    Fetches available topics, displays them, handles user selection
    and downloading. Returns when user goes back to main menu.
    """
    # Fetch the index
    index = _fetch_topics_index()
    if index is None:
        print(f"\n    {Fore.RED}Could not connect to the community topics repository.{Style.RESET_ALL}")
        print("    Check your internet connection and try again.\n")
        input("    Press Enter to return to the main menu...")
        return

    topics = index.get("topics", [])
    installed = _get_installed_topics()

    while True:
        _display_topics(topics, installed)

        if not topics:
            input("    Press Enter to return to the main menu...")
            return

        choice = input(f"    Select a topic (1-{len(topics)} or B): ").strip()

        if choice.lower() == "b":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(topics):
                selected = topics[idx]
                topic_id = selected.get("id", "")

                if topic_id in installed:
                    print(f"\n    '{selected.get('name', topic_id)}' is already installed.")
                    reinstall = input("    Re-download and update? (y/N): ").strip().lower()
                    if reinstall != "y":
                        continue

                success = _download_topic(selected)
                if success:
                    installed.add(topic_id)

                input("\n    Press Enter to continue...")
            else:
                print(f"    Please enter a number between 1 and {len(topics)}")
        except ValueError:
            print("    Please enter a valid number or B to go back")
