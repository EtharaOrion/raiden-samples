"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

import base64
import json
import os
import tempfile

import pytest


def _b64(s: bytes) -> str:
    return base64.b64encode(s).decode()


def _create_key(cli):
    r = cli("kms", "create-key")
    assert r.returncode == 0, r.stderr
    body = json.loads(r.stdout)
    return body["KeyMetadata"]["KeyId"]


def test_create_key_appears_in_list_keys_and_describe_key(cli):
    key_id = _create_key(cli)

    r_list = cli("kms", "list-keys")
    assert r_list.returncode == 0
    ids = [k["KeyId"] for k in json.loads(r_list.stdout)["Keys"]]
    assert key_id in ids

    r_desc = cli("kms", "describe-key", "--key-id", key_id)
    assert r_desc.returncode == 0
    assert json.loads(r_desc.stdout)["KeyMetadata"]["KeyId"] == key_id


def test_create_alias_appears_in_list_aliases_and_resolves(cli):
    key_id = _create_key(cli)
    alias_name = "alias/r2e-held-out-test"

    r = cli("kms", "create-alias", "--alias-name", alias_name, "--target-key-id", key_id)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "" or r.stdout.strip() == "{}" or json.loads(r.stdout) is not None

    r_list = cli("kms", "list-aliases")
    assert r_list.returncode == 0
    aliases = json.loads(r_list.stdout)["Aliases"]
    matched = [a for a in aliases if a["AliasName"] == alias_name]
    assert matched, f"alias {alias_name} not found in list-aliases output"
    assert matched[0]["TargetKeyId"] == key_id


def test_disable_key_visible_in_describe_and_blocks_encrypt(cli):
    key_id = _create_key(cli)

    r_dis = cli("kms", "disable-key", "--key-id", key_id)
    assert r_dis.returncode == 0, r_dis.stderr

    r_desc = cli("kms", "describe-key", "--key-id", key_id)
    assert r_desc.returncode == 0
    state = json.loads(r_desc.stdout)["KeyMetadata"]["KeyState"]
    assert state in ("Disabled",), f"unexpected key state after disable-key: {state}"

    r_enc = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", _b64(b"hello"))
    assert r_enc.returncode in (1, 254, 255)
    assert r_enc.stdout.strip() == ""
    assert r_enc.stderr.strip() != ""


def test_encrypt_decrypt_roundtrip(cli):
    key_id = _create_key(cli)
    plaintext = b"round-trip-secret-data"

    r_enc = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", _b64(plaintext))
    assert r_enc.returncode == 0, r_enc.stderr
    ciphertext_blob = json.loads(r_enc.stdout)["CiphertextBlob"]

    r_dec = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert r_dec.returncode == 0, r_dec.stderr
    dec_plain_b64 = json.loads(r_dec.stdout)["Plaintext"]
    assert base64.b64decode(dec_plain_b64) == plaintext


def test_generate_data_key_roundtrip(cli):
    key_id = _create_key(cli)

    r_gen = cli("kms", "generate-data-key", "--key-id", key_id, "--key-spec", "AES_256")
    assert r_gen.returncode == 0, r_gen.stderr
    body = json.loads(r_gen.stdout)
    ciphertext_blob = body["CiphertextBlob"]
    plaintext_b64 = body["Plaintext"]

    r_dec = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert r_dec.returncode == 0, r_dec.stderr
    dec_plain_b64 = json.loads(r_dec.stdout)["Plaintext"]
    assert dec_plain_b64 == plaintext_b64


def test_unknown_flag_is_client_usage_error(cli):
    r = cli("kms", "describe-key", "--key-id", "some-key", "--totally-unknown-flag", "x")
    assert r.returncode == 252
    assert r.stdout.strip() == ""
    assert r.stderr.strip() != ""


def test_missing_required_flag_is_client_usage_error(cli):
    r = cli("kms", "describe-key")
    assert r.returncode == 252
    assert r.stdout.strip() == ""
    assert r.stderr.strip() != ""


def test_unknown_subcommand_is_usage_error(cli):
    r = cli("kms", "totally-not-a-real-subcommand")
    assert r.returncode in (1, 252, 254, 255)
    assert r.stdout.strip() == ""
    assert r.stderr.strip() != ""


def test_unknown_service_is_usage_error(cli):
    r = cli("s3", "ls")
    assert r.returncode in (1, 252, 254, 255)
    assert r.stdout.strip() == ""
    assert r.stderr.strip() != ""


def test_bad_value_validation_is_delegated_to_service_not_client(cli):
    key_id = _create_key(cli)
    r = cli("kms", "schedule-key-deletion", "--key-id", key_id, "--pending-window-in-days", "99999")
    # value legality (out-of-range pending window) must be rejected by backend, not client
    assert r.returncode in (1, 254, 255), (
        f"expected a service-side error (not 252 usage error) for out-of-range value, got {r.returncode}: {r.stderr}"
    )
    assert r.stdout.strip() == ""
    assert r.stderr.strip() != ""


def test_plaintext_accepts_fileb_prefix(cli, tmp_path):
    key_id = _create_key(cli)
    plaintext = b"file-based-plaintext-blob"
    p = tmp_path / "pt.bin"
    p.write_bytes(plaintext)

    r_enc = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", f"fileb://{p}")
    assert r_enc.returncode == 0, r_enc.stderr
    ciphertext_blob = json.loads(r_enc.stdout)["CiphertextBlob"]

    r_dec = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert r_dec.returncode == 0, r_dec.stderr
    dec_plain_b64 = json.loads(r_dec.stdout)["Plaintext"]
    assert base64.b64decode(dec_plain_b64) == plaintext


def test_no_stdout_on_error_path(cli):
    r = cli("kms", "decrypt", "--ciphertext-blob", "not-valid-base64-ciphertext!!")
    assert r.returncode != 0
    assert r.stdout.strip() == "", "stdout must be empty on any failure path"
    assert "Traceback" not in r.stderr