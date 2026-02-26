import os
from pathlib import Path
from typing import Any

# Import loads .env via Data.config side effect.
from Data import config as _config  # noqa: F401

_tunnel: Any | None = None


def _as_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"SSH tunnel is enabled, but `{name}` is not set")
    return value


def start_ssh_tunnel_from_env(*, force: bool = False):
    global _tunnel

    if _tunnel is not None:
        return _tunnel

    if not force and not _as_bool(os.getenv("SSH_TUNNEL_ENABLED")):
        return None

    try:
        from sshtunnel import SSHTunnelForwarder
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "SSH tunnel support requires `sshtunnel`. Install dependencies from requirements.txt"
        ) from exc

    ssh_host = _get_required_env("SSH_HOST")
    ssh_port = int(os.getenv("SSH_PORT", "22"))
    ssh_user = _get_required_env("SSH_USER")
    ssh_key_path = _get_required_env("SSH_PRIVATE_KEY_PATH")
    ssh_key_passphrase = os.getenv("SSH_PRIVATE_KEY_PASSPHRASE") or None

    key_file = Path(ssh_key_path)
    if not key_file.exists():
        raise RuntimeError(f"SSH private key not found: {ssh_key_path}")

    local_host = os.getenv("SSH_LOCAL_BIND_HOST", "127.0.0.1")
    local_port = int(os.getenv("SSH_LOCAL_BIND_PORT", "55432"))
    remote_host = os.getenv("SSH_REMOTE_BIND_HOST", "127.0.0.1")
    remote_port = int(os.getenv("SSH_REMOTE_BIND_PORT", "5432"))

    tunnel = SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_pkey=str(key_file),
        ssh_private_key_password=ssh_key_passphrase,
        remote_bind_address=(remote_host, remote_port),
        local_bind_address=(local_host, local_port),
    )
    tunnel.start()
    _tunnel = tunnel

    print(
        f"[SSH] tunnel started: {local_host}:{tunnel.local_bind_port} -> "
        f"{remote_host}:{remote_port} via {ssh_user}@{ssh_host}:{ssh_port}"
    )
    return _tunnel


def stop_ssh_tunnel() -> None:
    global _tunnel
    if _tunnel is None:
        return
    try:
        _tunnel.stop()
        print("[SSH] tunnel stopped")
    finally:
        _tunnel = None
