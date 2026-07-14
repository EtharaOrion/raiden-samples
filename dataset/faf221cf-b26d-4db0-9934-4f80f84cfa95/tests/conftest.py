"""Session-scoped DynamoDB Local (compose sidecar) client + drop-all-tables reset
between tests. The engine is reached via AWS_ENDPOINT_URL_DYNAMODB, wired by
docker-compose to the ``ddb`` service at http://ddb:8000. The agent's submission
runs as a subprocess and inherits the same endpoint env.
"""

import ipaddress
import os
import socket as _socket
import subprocess
import sys
import time as _time

_R2E_ORIG_CONNECT = _socket.socket.connect
_R2E_BLOCKED_SUFFIXES = ('pypi.org', 'pythonhosted.org', 'github.com', 'githubusercontent.com', 'awscli.amazonaws.com', 's3.amazonaws.com', 'min.io', 'debian.org', 'ubuntu.com', 'pypi.tuna.tsinghua.edu.cn', 'pypi.mirrors.ustc.edu.cn', 'mirrors.aliyun.com', 'mirrors.cloud.tencent.com', 'pypi.douban.com', 'mirrors.huaweicloud.com', 'anaconda.com', 'anaconda.org', 'dynamodb.amazonaws.com',)


def _r2e_guarded_connect(self, address):
    if self.family in (_socket.AF_INET, _socket.AF_INET6) and isinstance(address, tuple):
        host = address[0]
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            for suffix in _R2E_BLOCKED_SUFFIXES:
                if host.lower() == suffix or host.lower().endswith("." + suffix):
                    raise RuntimeError(f"r2e:network-isolation: connect to {host!r} blocked")
        else:
            if not (ip.is_loopback or ip.is_private or ip.is_link_local):
                raise RuntimeError(
                    f"r2e:network-isolation: connect to public IP {host!r} blocked"
                )
    return _R2E_ORIG_CONNECT(self, address)


_socket.socket.connect = _r2e_guarded_connect
def _r2e_guarded_connect_ex(self, addr):
    import errno as _errno
    try:
        _r2e_guarded_connect(self, addr)
        return 0
    except RuntimeError:
        return _errno.EACCES
    except OSError as exc:
        return exc.errno
_socket.socket.connect_ex = _r2e_guarded_connect_ex

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from _ddb_http import DDBClient, DDBHTTPError  # noqa: E402


def pytest_configure(config):
    if not os.path.exists("/workspace/submission/aws"):
        pytest.exit(
            "Anti-NOP guard FAILED: submission entrypoint /workspace/submission/aws "
            "not found (no submission to evaluate). Reward=0.",
            returncode=1,
        )


@pytest.fixture(scope="session")
def _ddb_server():
    endpoint = (
        os.environ.get("AWS_ENDPOINT_URL_DYNAMODB")
        or os.environ.get("AWS_ENDPOINT_URL")
        or "http://ddb:8000"
    )
    client = DDBClient(endpoint_url=endpoint)
    # Defensive poll (~30s). Compose healthcheck normally gates us behind
    # `ddb: service_healthy`, but ad-hoc invocations may bypass that.
    for _ in range(300):
        try:
            client.list_tables()
            return endpoint
        except DDBHTTPError:
            return endpoint
        except OSError:
            _time.sleep(0.1)
    raise RuntimeError(f"dynamodb sidecar at {endpoint} not reachable within 30s")


@pytest.fixture
def ddb_client(_ddb_server):
    return DDBClient(endpoint_url=_ddb_server)


@pytest.fixture(autouse=True)
def _reset_ddb(ddb_client):
    ddb_client.reset_all_tables()
    yield
    ddb_client.reset_all_tables()


@pytest.fixture
def cli(_ddb_server):
    def _run(*args, env_overrides=None, timeout=60):
        env = os.environ.copy()
        env["AWS_ENDPOINT_URL_DYNAMODB"] = _ddb_server
        env["AWS_ENDPOINT_URL"] = _ddb_server
        env.setdefault("AWS_ACCESS_KEY_ID", "raidentest")
        env.setdefault("AWS_SECRET_ACCESS_KEY", "raidentest")
        env.setdefault("AWS_DEFAULT_REGION", "us-east-1")
        if env_overrides:
            env.update(env_overrides)
        return subprocess.run(
            ["/workspace/submission/aws", *args],
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    return _run
