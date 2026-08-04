"""Test fixtures for the aws cognito-idp CLI task (cognito_local backend, compose sidecar).

The cognito-idp backend runs as a compose SIDECAR (service "cognito"), reached over
the docker network at http://cognito:9229 (also exported as AWS_ENDPOINT_URL). The agent
submission runs as a subprocess; both it and the test reach the same sidecar via
AWS_ENDPOINT_URL_COGNITO_IDENTITY_PROVIDER (+ dummy AWS_* creds). Grading client is stdlib raw HTTP
(JSON 1.1, X-Amz-Target AWSCognitoIdentityProviderService) — no AWS SDK.
"""

import ipaddress
import json as _json
import os
import socket as _socket
import subprocess
import sys
import time as _time
import urllib.request as _ureq
import urllib.error as _uerr

_ORIG_CONNECT = _socket.socket.connect
_BLOCKED_SUFFIXES = ('pypi.org', 'pythonhosted.org', 'github.com', 'githubusercontent.com', 'awscli.amazonaws.com', 's3.amazonaws.com', 'min.io', 'debian.org', 'ubuntu.com', 'pypi.tuna.tsinghua.edu.cn', 'pypi.mirrors.ustc.edu.cn', 'mirrors.aliyun.com', 'mirrors.cloud.tencent.com', 'pypi.douban.com', 'mirrors.huaweicloud.com', 'anaconda.com', 'anaconda.org',)


def _guarded_connect(self, address):
    if self.family in (_socket.AF_INET, _socket.AF_INET6) and isinstance(address, tuple):
        host = address[0]
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            for suffix in _BLOCKED_SUFFIXES:
                if host.lower() == suffix or host.lower().endswith("." + suffix):
                    raise RuntimeError(f"network-isolation: connect to {host!r} blocked")
        else:
            if not (ip.is_loopback or ip.is_private):
                raise RuntimeError(f"network-isolation: connect to public IP {host!r} blocked")
    return _ORIG_CONNECT(self, address)


_socket.socket.connect = _guarded_connect
def _guarded_connect_ex(self, addr):
    import errno as _errno
    try:
        _guarded_connect(self, addr)
        return 0
    except RuntimeError:
        return _errno.EACCES
    except OSError as exc:
        return exc.errno
_socket.socket.connect_ex = _guarded_connect_ex

import pytest


def pytest_configure(config):
    if not os.path.exists("/workspace/submission/aws"):
        pytest.exit(
            "Anti-NOP guard FAILED: submission entrypoint /workspace/submission/aws "
            "not found (no submission to evaluate). Score=0.",
            returncode=1,
        )


_AUTH = (
    "AWS4-HMAC-SHA256 Credential=dummy/20260101/us-east-1/cognito-idp/aws4_request, "
    "SignedHeaders=host;x-amz-date, Signature=dummy"
)


class _Client:
    """Minimal stdlib JSON-protocol client (raw HTTP; the local backend ignores SigV4)."""

    def __init__(self, endpoint):
        self.endpoint = endpoint.rstrip("/") + "/"

    def rpc(self, action, payload=None, timeout=30):
        req = _ureq.Request(
            self.endpoint,
            data=_json.dumps(payload or {}).encode(),
            method="POST",
            headers={
                "Content-Type": "application/x-amz-json-1.1",
                "X-Amz-Target": "AWSCognitoIdentityProviderService." + action,
                "X-Amz-Date": "20260101T000000Z",
                "Authorization": _AUTH,
            },
        )
        with _ureq.urlopen(req, timeout=timeout) as r:
            return _json.loads(r.read() or b"{}")


@pytest.fixture(scope="session")
def _server():
    # The cognito-idp backend is a compose sidecar; connect over the docker network
    # (no in-process boot). depends_on/healthcheck may not be honored by every runner,
    # so poll defensively until the sidecar accepts requests (~90s — cold qemu
    # starts under parallel generation load exceed 30s).
    endpoint = os.environ.get("AWS_ENDPOINT_URL_COGNITO_IDENTITY_PROVIDER") or os.environ.get("AWS_ENDPOINT_URL") or "http://cognito:9229"
    _c = _Client(endpoint)
    for _ in range(450):
        try:
            _c.rpc("ListUserPools", {})
            break
        except _uerr.HTTPError:
            break  # server answered (up)
        except OSError:
            _time.sleep(0.2)
    else:
        raise RuntimeError("cognito-idp sidecar at " + endpoint + " not reachable within 90s")
    yield endpoint


@pytest.fixture
def cognito(_server):
    return _Client(_server)


@pytest.fixture(autouse=True)
def _reset_backend(_server):
    _c = _Client(_server)
    try:
        for _p in _c.rpc('ListUserPools', {'MaxResults': 60}).get('UserPools', []):
            try:
                _c.rpc('DeleteUserPool', {'UserPoolId': _p['Id']})
            except Exception:
                pass
    except Exception:
        pass
    yield

@pytest.fixture
def cli(_server):
    def _run(*args, env_overrides=None, timeout=120):
        env = os.environ.copy()
        env["AWS_ENDPOINT_URL_COGNITO_IDENTITY_PROVIDER"] = _server
        env["AWS_ENDPOINT_URL"] = _server
        env.setdefault("AWS_ACCESS_KEY_ID", "dummy")
        env.setdefault("AWS_SECRET_ACCESS_KEY", "dummy")
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
