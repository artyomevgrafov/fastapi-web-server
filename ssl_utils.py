"""SSL/TLS Certificate Utilities for FastAPI Server"""

import ssl
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


class SSLCertificateManager:
    """Manage SSL/TLS certificates for FastAPI server"""

    def __init__(self, certs_dir: str = "certs") -> None:
        self.certs_dir: Path = Path(certs_dir)
        self.certs_dir.mkdir(exist_ok=True)

        # Default certificate paths
        self.cert_file: Path = self.certs_dir / "cert.pem"
        self.key_file: Path = self.certs_dir / "key.pem"
        self.ca_file: Path = self.certs_dir / "ca.pem"

    def generate_self_signed_certificate(
        self,
        common_name: str = "localhost",
        country: str = "US",
        state: str = "State",
        locality: str = "City",
        organization: str = "Organization",
        organizational_unit: str = "IT",
        validity_days: int = 365,
        key_size: int = 2048,
    ) -> Tuple[bool, str]:
        """
        Generate a self-signed SSL certificate using OpenSSL

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            # Check if OpenSSL is available
            if not self._check_openssl_available():
                return False, "OpenSSL is not available. Please install OpenSSL."

            # Generate private key
            key_cmd = ["openssl", "genrsa", "-out", str(self.key_file), str(key_size)]

            _ = subprocess.run(key_cmd, check=True, capture_output=True)

            # Create certificate configuration
            config_content = self._create_cert_config(
                common_name=common_name,
                country=country,
                state=state,
                locality=locality,
                organization=organization,
                organizational_unit=organizational_unit,
            )

            config_file = self.certs_dir / "cert.conf"
            with open(config_file, "w") as f:
                f.write(config_content)

            # Generate certificate signing request
            csr_file = self.certs_dir / "request.csr"
            csr_cmd = [
                "openssl",
                "req",
                "-new",
                "-key",
                str(self.key_file),
                "-out",
                str(csr_file),
                "-config",
                str(config_file),
            ]

            _ = subprocess.run(csr_cmd, check=True, capture_output=True)

            # Generate self-signed certificate
            cert_cmd = [
                "openssl",
                "x509",
                "-req",
                "-in",
                str(csr_file),
                "-signkey",
                str(self.key_file),
                "-out",
                str(self.cert_file),
                "-days",
                str(validity_days),
                "-extensions",
                "v3_req",
                "-extfile",
                str(config_file),
            ]

            _ = subprocess.run(cert_cmd, check=True, capture_output=True)

            # Clean up temporary files
            config_file.unlink(missing_ok=True)
            csr_file.unlink(missing_ok=True)

            return (
                True,
                f"Self-signed certificate generated successfully:\n"
                f"  Certificate: {self.cert_file}\n"
                f"  Private Key: {self.key_file}\n"
                f"  Valid for: {validity_days} days",
            )

        except subprocess.CalledProcessError as e:
            return False, f"OpenSSL command failed: {e}"
        except Exception as e:
            return False, f"Certificate generation failed: {e}"

    def _check_openssl_available(self) -> bool:
        """Check if OpenSSL is available in the system"""
        try:
            _ = subprocess.run(["openssl", "version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _create_cert_config(
        self,
        common_name: str,
        country: str,
        state: str,
        locality: str,
        organization: str,
        organizational_unit: str,
    ) -> str:
        """Create OpenSSL configuration file content"""
        return f"""
[ req ]
default_bits        = 2048
distinguished_name  = req_distinguished_name
req_extensions      = v3_req
prompt              = no

[ req_distinguished_name ]
C                   = {country}
ST                  = {state}
L                   = {locality}
O                   = {organization}
OU                  = {organizational_unit}
CN                  = {common_name}

[ v3_req ]
basicConstraints    = CA:FALSE
keyUsage            = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage    = serverAuth
subjectAltName      = @alt_names

[ alt_names ]
DNS.1               = {common_name}
DNS.2               = localhost
IP.1                = 127.0.0.1
IP.2                = ::1
"""

    def validate_certificate_files(self) -> Tuple[bool, str]:
        """
        Validate existing certificate and key files

        Returns:
            tuple[bool, str]: (valid, message)
        """
        if not self.cert_file.exists():
            return False, f"Certificate file not found: {self.cert_file}"

        if not self.key_file.exists():
            return False, f"Private key file not found: {self.key_file}"

        try:
            # Try to load the certificate
            with open(self.cert_file, "rb") as f:
                cert_data = f.read()

            # Try to load the private key
            with open(self.key_file, "rb") as f:
                key_data = f.read()

            # Basic validation - check if files are not empty
            if len(cert_data) == 0:
                return False, "Certificate file is empty"

            if len(key_data) == 0:
                return False, "Private key file is empty"

            return True, "Certificate files are valid"

        except Exception as e:
            return False, f"Error reading certificate files: {e}"

    def get_certificate_info(self) -> Optional[dict[str, str]]:
        """Get information about the certificate"""
        if not self.cert_file.exists():
            return None

        try:
            # Use OpenSSL to get certificate information
            cmd = [
                "openssl",
                "x509",
                "-in",
                str(self.cert_file),
                "-noout",
                "-subject",
                "-issuer",
                "-dates",
                "-serial",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout

            info: dict[str, str] = {}
            for line in output.split("\n"):
                if "subject=" in line:
                    info["subject"] = line.replace("subject=", "").strip()
                elif "issuer=" in line:
                    info["issuer"] = line.replace("issuer=", "").strip()
                elif "notBefore=" in line:
                    info["not_before"] = line.replace("notBefore=", "").strip()
                elif "notAfter=" in line:
                    info["not_after"] = line.replace("notAfter=", "").strip()
                elif "serial=" in line:
                    info["serial"] = line.replace("serial=", "").strip()

            return info

        except Exception:
            return None

    def create_ssl_context(
        self, verify_mode: str = "CERT_REQUIRED"
    ) -> Optional[ssl.SSLContext]:
        """
        Create SSL context for the server

        Args:
            verify_mode: SSL verification mode (CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED)

        Returns:
            SSLContext or None if certificate files are invalid
        """
        if not self.validate_certificate_files()[0]:
            return None

        try:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(
                certfile=str(self.cert_file),
                keyfile=str(self.key_file),
                password=None,  # Add password support if needed
            )

            # Set verification mode
            if verify_mode == "CERT_NONE":
                context.verify_mode = ssl.CERT_NONE
            elif verify_mode == "CERT_OPTIONAL":
                context.verify_mode = ssl.CERT_OPTIONAL
            else:  # CERT_REQUIRED
                context.verify_mode = ssl.CERT_REQUIRED

            # Load CA certificates if provided
            if self.ca_file.exists():
                context.load_verify_locations(cafile=str(self.ca_file))

            return context

        except Exception as e:
            print(f"Error creating SSL context: {e}")
            return None

    def cleanup(self):
        """Clean up certificate files"""
        files_to_remove = [
            self.cert_file,
            self.key_file,
            self.ca_file,
            self.certs_dir / "cert.conf",
            self.certs_dir / "request.csr",
        ]

        for file_path in files_to_remove:
            file_path.unlink(missing_ok=True)

        # Remove directory if empty
        try:
            self.certs_dir.rmdir()
        except OSError:
            pass  # Directory not empty


def setup_ssl_certificates(
    certs_dir: str = "certs", force_regenerate: bool = False, **cert_params
) -> tuple[bool, str]:
    """
    Setup SSL certificates for the server

    Args:
        certs_dir: Directory to store certificates
        force_regenerate: Force regeneration even if certificates exist
        **cert_params: Additional parameters for certificate generation

    Returns:
        tuple[bool, str]: (success, message)
    """
    manager = SSLCertificateManager(certs_dir)

    # Check if certificates already exist
    if not force_regenerate:
        valid, message = manager.validate_certificate_files()
        if valid:
            return True, f"Using existing certificates: {message}"

    # Generate new certificates
    success, message = manager.generate_self_signed_certificate(**cert_params)  # type: ignore

    if success:
        # Validate the generated certificates
        valid, validation_msg = manager.validate_certificate_files()
        if not valid:
            return False, f"Generated certificates are invalid: {validation_msg}"

    return success, message


if __name__ == "__main__":
    # Test certificate generation
    success, message = setup_ssl_certificates()
    if success:
        print("✅ SSL certificates setup successfully")
        print(message)

        # Display certificate info
        manager = SSLCertificateManager()
        info = manager.get_certificate_info()
        if info:
            print("\n📄 Certificate Information:")
            for key, value in info.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
    else:
        print("❌ SSL certificates setup failed")
        print(message)
        sys.exit(1)
