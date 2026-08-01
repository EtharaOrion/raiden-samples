"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""Held-out pytest module for the `aws kms` CLI emulation task.

Uses only the `cli` fixture provided by conftest.py (subprocess invocation of
the submission entry point). Assertions are derived strictly from the
documented behavioral contract (TRUTH.md), not from any specific
implementation's internals.
"""
import base64
import json
import uuid

import pytest


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _unique(prefix="alias/test"):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _create_key(cli):
    r = cli("kms", "create-key")
    assert r.returncode == 0, r.stderr
    body = json.loads(r.stdout)
    return body["KeyMetadata"]["KeyId"]


def test_unknown_command_is_usage_error(cli):
    r = cli("kms", "totally-not-a-real-command")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""
    assert "Traceback" not in r.stderr


def test_missing_required_arg_is_usage_error(cli):
    # create-alias requires --alias-name and --target-key-id
    r = cli("kms", "create-alias")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""
    assert "Traceback" not in r.stderr


def test_create_key_success_shape_and_visibility(cli):
    r = cli("kms", "create-key")
    assert r.returncode == 0
    assert r.stderr == ""
    body = json.loads(r.stdout)  # must parse as JSON
    key_id = body["KeyMetadata"]["KeyId"]

    d = cli("kms", "describe-key", "--key-id", key_id)
    assert d.returncode == 0, d.stderr
    dbody = json.loads(d.stdout)
    assert dbody["KeyMetadata"]["KeyId"] == key_id

    lk = cli("kms", "list-keys")
    assert lk.returncode == 0, lk.stderr
    lbody = json.loads(lk.stdout)
    ids = [k["KeyId"] for k in lbody.get("Keys", [])]
    assert key_id in ids


def test_encrypt_decrypt_roundtrip(cli):
    key_id = _create_key(cli)
    plaintext = _b64(b"super-secret-payload-42")

    enc = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)
    assert enc.returncode == 0, enc.stderr
    assert enc.stderr == ""
    ebody = json.loads(enc.stdout)
    ciphertext = ebody["CiphertextBlob"]
    assert ebody["KeyId"] in (key_id, key_id.split("/")[-1]) or key_id in ebody["KeyId"]

    dec = cli("kms", "decrypt", "--ciphertext-blob", ciphertext)
    assert dec.returncode == 0, dec.stderr
    dbody = json.loads(dec.stdout)
    assert dbody["Plaintext"] == plaintext
    assert key_id in dbody["KeyId"]


def test_disable_key_blocks_crypto_then_enable_restores(cli):
    key_id = _create_key(cli)
    plaintext = _b64(b"blocked-when-disabled")

    dis = cli("kms", "disable-key", "--key-id", key_id)
    assert dis.returncode == 0, dis.stderr

    fail = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)
    assert fail.returncode != 0
    assert fail.stdout == ""
    assert fail.stderr.strip() != ""
    assert "Traceback" not in fail.stderr

    en = cli("kms", "enable-key", "--key-id", key_id)
    assert en.returncode == 0, en.stderr

    ok = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)
    assert ok.returncode == 0, ok.stderr
    assert json.loads(ok.stdout)["CiphertextBlob"]


def test_schedule_and_cancel_key_deletion_state_machine(cli):
    key_id = _create_key(cli)

    sched = cli("kms", "schedule-key-deletion", "--key-id", key_id)
    assert sched.returncode == 0, sched.stderr

    desc = cli("kms", "describe-key", "--key-id", key_id)
    assert desc.returncode == 0
    state = json.loads(desc.stdout)["KeyMetadata"].get("KeyState", "")
    assert "PendingDeletion" in state

    blocked = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", _b64(b"x"))
    assert blocked.returncode != 0
    assert blocked.stdout == ""

    cancel = cli("kms", "cancel-key-deletion", "--key-id", key_id)
    assert cancel.returncode == 0, cancel.stderr

    desc2 = cli("kms", "describe-key", "--key-id", key_id)
    state2 = json.loads(desc2.stdout)["KeyMetadata"].get("KeyState", "")
    assert state2 == "Disabled"
    assert state2 != "Enabled"

    still_blocked = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", _b64(b"x"))
    assert still_blocked.returncode != 0

    en = cli("kms", "enable-key", "--key-id", key_id)
    assert en.returncode == 0, en.stderr
    restored = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", _b64(b"x"))
    assert restored.returncode == 0, restored.stderr


def test_alias_lifecycle_and_duplicate_error(cli):
    key_id = _create_key(cli)
    alias_name = _unique()

    create = cli("kms", "create-alias", "--alias-name", alias_name, "--target-key-id", key_id)
    assert create.returncode == 0, create.stderr
    assert create.stdout == "" or json.loads(create.stdout) is not None

    lst = cli("kms", "list-aliases")
    assert lst.returncode == 0, lst.stderr
    names = [a["AliasName"] for a in json.loads(lst.stdout).get("Aliases", [])]
    assert alias_name in names

    dup = cli("kms", "create-alias", "--alias-name", alias_name, "--target-key-id", key_id)
    assert dup.returncode != 0
    assert dup.stdout == ""
    assert dup.stderr.strip() != ""

    delete = cli("kms", "delete-alias", "--alias-name", alias_name)
    assert delete.returncode == 0, delete.stderr

    lst2 = cli("kms", "list-aliases")
    names2 = [a["AliasName"] for a in json.loads(lst2.stdout).get("Aliases", [])]
    assert alias_name not in names2


def test_alias_targeting_missing_key_errors(cli):
    alias_name = _unique()
    r = cli("kms", "create-alias", "--alias-name", alias_name, "--target-key-id", "nonexistent-key-id-zzz")
    assert r.returncode != 0
    assert r.stdout == ""
    assert r.stderr.strip() != ""
    assert "Traceback" not in r.stderr


def test_operations_on_nonexistent_key_are_not_found(cli):
    bogus = "00000000-0000-0000-0000-000000000000"
    for args in (
        ("kms", "describe-key", "--key-id", bogus),
        ("kms", "disable-key", "--key-id", bogus),
        ("kms", "encrypt", "--key-id", bogus, "--plaintext", _b64(b"x")),
    ):
        r = cli(*args)
        assert r.returncode != 0
        assert r.stdout == ""
        assert r.stderr.strip() != ""
        assert "Traceback" not in r.stderr


def test_no_credential_or_region_hardcode_env_respected(cli):
    # Passing a bogus endpoint override should not silently succeed against
    # the real backend if the CLI truly reads endpoint config from env;
    # this at least verifies the CLI does not crash with a raw traceback
    # and produces a clean error/usage-class exit when env is broken.
    r = cli(
        "kms",
        "list-keys",
        env_overrides={"AWS_ENDPOINT_URL_KMS": "http://127.0.0.1:1", "AWS_ENDPOINT_URL": "http://127.0.0.1:1"},
    )
    assert r.returncode != 0
    assert "Traceback" not in r.stderr
    assert r.stdout == ""