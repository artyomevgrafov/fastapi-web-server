#!/usr/bin/env python3
"""
SSL/TLS Certificate Management Script for FastAPI Server
Provides command-line interface for managing SSL certificates
"""

import argparse
import sys
from pathlib import Path
from ssl_utils import SSLCertificateManager, setup_ssl_certificates


def main():
    """Main function for SSL certificate management"""
    parser = argparse.ArgumentParser(
        description="Manage SSL/TLS certificates for FastAPI server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate self-signed certificate
  python manage_ssl.py generate

  # Generate with custom parameters
  python manage_ssl.py generate --common-name "example.com" --validity-days 730

  # Validate existing certificates
  python manage_ssl.py validate

  # Show certificate information
  python manage_ssl.py info

  # Clean up certificate files
  python manage_ssl.py cleanup
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate SSL certificates"
    )
    generate_parser.add_argument(
        "--certs-dir", default="certs", help="Certificate directory"
    )
    generate_parser.add_argument(
        "--common-name", default="localhost", help="Common Name (CN)"
    )
    generate_parser.add_argument("--country", default="US", help="Country code")
    generate_parser.add_argument("--state", default="State", help="State or province")
    generate_parser.add_argument("--locality", default="City", help="Locality or city")
    generate_parser.add_argument(
        "--organization", default="FastAPI Server", help="Organization name"
    )
    generate_parser.add_argument(
        "--organizational-unit", default="IT", help="Organizational unit"
    )
    generate_parser.add_argument(
        "--validity-days", type=int, default=365, help="Certificate validity in days"
    )
    generate_parser.add_argument(
        "--key-size", type=int, default=2048, help="RSA key size"
    )
    generate_parser.add_argument(
        "--force", action="store_true", help="Force regeneration"
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate SSL certificates"
    )
    validate_parser.add_argument(
        "--certs-dir", default="certs", help="Certificate directory"
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Show certificate information")
    info_parser.add_argument(
        "--certs-dir", default="certs", help="Certificate directory"
    )

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Remove certificate files")
    cleanup_parser.add_argument(
        "--certs-dir", default="certs", help="Certificate directory"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = SSLCertificateManager(args.certs_dir)

    if args.command == "generate":
        print("🔐 Generating SSL certificates...")

        if not args.force:
            valid, message = manager.validate_certificate_files()
            if valid:
                print("ℹ️  Certificates already exist. Use --force to regenerate.")
                return

        success, message = manager.generate_self_signed_certificate(
            common_name=args.common_name,
            country=args.country,
            state=args.state,
            locality=args.locality,
            organization=args.organization,
            organizational_unit=args.organizational_unit,
            validity_days=args.validity_days,
            key_size=args.key_size,
        )

        if success:
            print("✅ " + message)

            # Show certificate info
            info = manager.get_certificate_info()
            if info:
                print("\n📄 Certificate Information:")
                for key, value in info.items():
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print("❌ " + message)
            sys.exit(1)

    elif args.command == "validate":
        print("🔍 Validating SSL certificates...")
        valid, message = manager.validate_certificate_files()

        if valid:
            print("✅ " + message)

            # Additional OpenSSL validation
            info = manager.get_certificate_info()
            if info:
                print("\n📄 Certificate Details:")
                for key, value in info.items():
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print("❌ " + message)
            sys.exit(1)

    elif args.command == "info":
        print("📄 SSL Certificate Information:")
        info = manager.get_certificate_info()

        if info:
            for key, value in info.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print("❌ No certificate information available")
            print("   Generate certificates first with: python manage_ssl.py generate")
            sys.exit(1)

    elif args.command == "cleanup":
        print("🧹 Cleaning up SSL certificates...")
        manager.cleanup()
        print("✅ Certificate files removed")

    else:
        parser.print_help()


def interactive_setup():
    """Interactive SSL certificate setup"""
    print("🔐 Interactive SSL Certificate Setup")
    print("=" * 40)

    manager = SSLCertificateManager()

    # Check existing certificates
    valid, message = manager.validate_certificate_files()
    if valid:
        print("✅ Existing certificates found:")
        info = manager.get_certificate_info()
        if info:
            for key, value in info.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")

        response = input("\n❓ Regenerate certificates? (y/N): ").lower().strip()
        if response != "y":
            print("ℹ️  Using existing certificates")
            return

    print("\n📝 Certificate Parameters:")
    common_name = input(f"  Common Name [localhost]: ").strip() or "localhost"
    country = input(f"  Country Code [US]: ").strip() or "US"
    state = input(f"  State [State]: ").strip() or "State"
    locality = input(f"  Locality [City]: ").strip() or "City"
    organization = (
        input(f"  Organization [FastAPI Server]: ").strip() or "FastAPI Server"
    )
    organizational_unit = input(f"  Organizational Unit [IT]: ").strip() or "IT"

    try:
        validity_days = int(input(f"  Validity Days [365]: ").strip() or "365")
    except ValueError:
        validity_days = 365

    print(f"\n📋 Summary:")
    print(f"  Common Name: {common_name}")
    print(f"  Country: {country}")
    print(f"  State: {state}")
    print(f"  Locality: {locality}")
    print(f"  Organization: {organization}")
    print(f"  Organizational Unit: {organizational_unit}")
    print(f"  Validity: {validity_days} days")

    confirm = (
        input("\n❓ Generate certificates with these settings? (Y/n): ").lower().strip()
    )
    if confirm == "n":
        print("❌ Certificate generation cancelled")
        return

    print("\n🔐 Generating certificates...")
    success, message = manager.generate_self_signed_certificate(
        common_name=common_name,
        country=country,
        state=state,
        locality=locality,
        organization=organization,
        organizational_unit=organizational_unit,
        validity_days=validity_days,
    )

    if success:
        print("✅ " + message)
    else:
        print("❌ " + message)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        interactive_setup()
    else:
        main()
