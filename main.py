#!/usr/bin/env python3
"""
CertQuest - Multi-Certification Training Framework

A modular quiz game for certification exam preparation.
Add new certifications by dropping folders into /certifications/
"""

import sys
import os

# Ensure we can import from the engine directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.certification_loader import CertificationLoader


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_banner():
    """Display the CertQuest banner."""
    banner = r"""
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                           ║
    ║       ██████╗███████╗██████╗ ████████╗ ██████╗ ██╗   ██╗███████╗███████╗  ║
    ║      ██╔════╝██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██║   ██║██╔════╝╚══██╔══╝  ║
    ║      ██║     █████╗  ██████╔╝   ██║   ██║   ██║██║   ██║█████╗     ██║     ║
    ║      ██║     ██╔══╝  ██╔══██╗   ██║   ██║▄▄ ██║██║   ██║██╔══╝     ██║     ║
    ║      ╚██████╗███████╗██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗   ██║     ║
    ║       ╚═════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚══▀▀═╝  ╚═════╝ ╚══════╝   ╚═╝     ║
    ║                                                                           ║
    ║               Multi-Certification Training Framework                      ║
    ║                                                                           ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def show_certification_menu(certifications):
    """Display available certifications and get user selection."""
    print("\n    Available Certifications:\n")

    if not certifications:
        print("    No certifications found!")
        print("    Add certification packs to the /certifications/ folder.")
        return None

    for i, cert in enumerate(certifications, 1):
        name = cert['name']
        full_name = cert.get('full_name', '')
        org = cert.get('organization', '')
        domains = cert.get('domain_count', 0)

        print(f"    [{i}] {name}")
        if full_name:
            print(f"        {full_name}")
        if org:
            print(f"        Organization: {org}")
        print(f"        Domains: {domains}")
        print()

    print(f"    [D] Download Community Topics")
    print(f"    [Q] Quit\n")

    while True:
        try:
            choice = input("    Select a certification (1-{}, D, or Q): ".format(len(certifications))).strip()

            if choice.lower() == 'q':
                return None

            if choice.lower() == 'd':
                return 'download'

            index = int(choice) - 1
            if 0 <= index < len(certifications):
                return certifications[index]
            else:
                print(f"    Please enter a number between 1 and {len(certifications)}")
        except ValueError:
            print("    Please enter a valid number, D for downloads, or Q to quit")


def main():
    """Main entry point for CertQuest."""
    while True:
        clear_screen()
        show_banner()

        # Discover available certifications
        loader = CertificationLoader()
        certifications = loader.discover_certifications()

        # Let user select a certification
        selected = show_certification_menu(certifications)

        if selected is None:
            print("\n    Farewell, knowledge seeker!\n")
            sys.exit(0)

        # Handle community topic downloads
        if selected == 'download':
            from engine.topic_downloader import run_topic_browser
            run_topic_browser()
            continue  # Return to main menu after download

        print(f"\n    Loading {selected['name']}...")

        # Load the full certification
        try:
            cert_config = loader.load_certification(selected['id'])
        except FileNotFoundError as e:
            print(f"\n    Error: {e}")
            input("\n    Press Enter to continue...")
            continue
        except Exception as e:
            print(f"\n    Error loading certification: {e}")
            input("\n    Press Enter to continue...")
            continue

        # Start the game
        from engine.game import Game
        game = Game(cert_config)

        try:
            game.run()
        except KeyboardInterrupt:
            print("\n\n    Your journey has been interrupted. Farewell!\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
