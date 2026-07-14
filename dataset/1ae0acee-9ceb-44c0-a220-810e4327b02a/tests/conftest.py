"""Per-session MinIO S3 server + per-test bucket-wipe fixtures.

The agent's submission is exposed as `aws` on $PATH and invoked as a
subprocess; in-process patching cannot reach subprocesses, so we boot a real
MinIO server once per session on a random port and point boto3 (in both the
test and the subprocess) at it via AWS_ENDPOINT_URL_S3.
"""

import os
import shutil
import socket
import subprocess
import time

import pytest
import requests

from _s3_http import S3Client

RC_SUCCESS = 0
RC_OP_ERROR = 1
RC_TRANSFER_WARN = 2
RC_PARAM_ERROR = 252
RC_CONFIG_ERROR = 253
RC_CLIENT_ERROR = 254
RC_GENERAL = 255

ALLOWED_ERROR_CODES = (
    "NoSuchBucket",
    "NoSuchKey",
    "BucketAlreadyExists",
    "BucketAlreadyOwnedByYou",
    "InvalidBucketName",
    "BucketNotEmpty",
    "AccessDenied",
    "InvalidRequest",
    "InvalidArgument",
    "InvalidS3URI",
)
_FAILURE_PHRASES = (
    " failed",
    "does not exist",
    "no such",
    "not found",
    "an error occurred",
    "cannot",
    "invalid",
    "unable",
    "could not",
    "must be",
    "is required",
    "usage",
    "unknown",
    "parameter validation",
    "are required",
    "unrecognized",
)


def _stderr_names_error(stderr: str) -> bool:
    """True if stderr surfaces an AWS error class or generic failure phrase."""
    lower = stderr.lower()
    if any(code.lower() in lower for code in ALLOWED_ERROR_CODES):
        return True
    return any(p in lower for p in _FAILURE_PHRASES)


def pytest_configure(config):
    if shutil.which("aws") is None:
        pytest.exit(
            "Anti-NOP guard FAILED: no `aws` executable on $PATH "
            "(no submission to evaluate). Reward=0.",
            returncode=1,
        )
    if shutil.which("minio") is None:
        pytest.exit(
            "MinIO server binary not found on $PATH. Reward=0.",
            returncode=1,
        )


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_ready(endpoint: str, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            r = requests.get(f"{endpoint}/minio/health/live", timeout=0.5)
            if r.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.1)
    raise RuntimeError(f"MinIO server at {endpoint} did not become ready within {timeout}s")


@pytest.fixture(scope="session")
def _minio_server(tmp_path_factory):
    data_dir = tmp_path_factory.mktemp("minio-data")
    port = _free_port()
    env = {
            **os.environ,
            "MINIO_ROOT_USER": "raidentest",
            "MINIO_ROOT_PASSWORD": "raidentest",
            "MINIO_CI_CD": "on",
            "MINIO_BROWSER": "off",
            "MINIO_KMS_SECRET_KEY": "foo:IyqsE3sBqcMSlonhAxfqLK1kHhIzy+xvyJZbfFbcHT4=",
        }
    proc = subprocess.Popen(
        [
            "minio", "server", str(data_dir),
            "--address", f":{port}",
            "--console-address", ":0",
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    endpoint = f"http://127.0.0.1:{port}"
    try:
        _wait_ready(endpoint)
    except Exception:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        raise
    try:
        yield endpoint
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def _wipe_state(endpoint: str) -> None:
    client = S3Client(endpoint_url=endpoint)
    for b in client.list_buckets()["Buckets"]:
        name = b["Name"]
        for obj in client.list_objects_v2(Bucket=name).get("Contents", []):
            client.delete_object(Bucket=name, Key=obj["Key"])
        client.delete_bucket(Bucket=name)


@pytest.fixture(autouse=True)
def _reset_minio_state(_minio_server):
    _wipe_state(_minio_server)
    yield
    _wipe_state(_minio_server)


@pytest.fixture
def minio_server(_minio_server):
    return _minio_server


@pytest.fixture
def s3_client(minio_server):
    return S3Client(endpoint_url=minio_server)


@pytest.fixture
def cli(minio_server):
    """Invoke the submission's `aws` on $PATH as a subprocess.

    Returns a callable: cli(*argv) -> subprocess.CompletedProcess
    """

    def _run(*args, env_overrides=None, timeout=60):
        env = os.environ.copy()
        env["AWS_ENDPOINT_URL_S3"] = minio_server
        env["AWS_ENDPOINT_URL"] = minio_server
        env["AWS_ACCESS_KEY_ID"] = "raidentest"
        env["AWS_SECRET_ACCESS_KEY"] = "raidentest"
        env["AWS_DEFAULT_REGION"] = "us-east-1"
        pp = [p for p in env.get("PYTHONPATH", "").split(":") if p and p != "/opt/test-libs"]
        if pp:
            env["PYTHONPATH"] = ":".join(pp)
        else:
            env.pop("PYTHONPATH", None)
        if env_overrides:
            env.update(env_overrides)
        return subprocess.run(
            ["aws", *args],
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    return _run
