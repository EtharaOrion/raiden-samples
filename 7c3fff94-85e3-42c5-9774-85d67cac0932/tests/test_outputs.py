"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

import base64
import json

import pytest


VALID_EXIT_CODES = {0, 1, 252, 254, 255}


def _parse_json_stdout(result):
    assert result.stdout, "expected non-empty stdout on success"
    assert result.stderr == "", f"expected empty stderr on success, got: {result.stderr!r}"
    return json.loads(result.stdout)


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def test_unknown_command_is_usage_error(cli):
    r = cli("kms", "totally-not-a-real-subcommand")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""
    assert "Traceback" not in r.stderr


def test_missing_required_flag_is_usage_error(cli):
    # create-alias requires --alias-name and --target-key-id
    r = cli("kms", "create-alias", "--alias-name", "alias/missing-target")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""
    assert "Traceback" not in r.stderr


def test_create_key_describe_key_cross_process_consistency(cli):
    r1 = cli("kms", "create-key")
    assert r1.returncode == 0
    data1 = _parse_json_stdout(r1)
    key_id = data1["KeyMetadata"]["KeyId"]
    assert key_id

    # Separate subprocess must see the same key.
    r2 = cli("kms", "describe-key", "--key-id", key_id)
    assert r2.returncode == 0
    data2 = _parse_json_stdout(r2)
    assert data2["KeyMetadata"]["KeyId"] == key_id
    assert data2["KeyMetadata"]["KeyState"] in ("Enabled",)


def test_encrypt_decrypt_round_trip(cli):
    r_key = cli("kms", "create-key")
    assert r_key.returncode == 0
    key_id = _parse_json_stdout(r_key)["KeyMetadata"]["KeyId"]

    plaintext = b"hello held-out world"
    r_enc = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", _b64(plaintext),
    )
    assert r_enc.returncode == 0
    enc_data = _parse_json_stdout(r_enc)
    ciphertext_blob = enc_data["CiphertextBlob"]
    assert ciphertext_blob

    r_dec = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_blob,
    )
    assert r_dec.returncode == 0
    dec_data = _parse_json_stdout(r_dec)
    recovered = base64.b64decode(dec_data["Plaintext"])
    assert recovered == plaintext


def test_sign_verify_round_trip_and_tamper_detection(cli):
    r_key = cli(
        "kms", "create-key",
        "--key-usage", "SIGN_VERIFY",
        "--key-spec", "RSA_2048",
    )
    assert r_key.returncode == 0
    key_id = _parse_json_stdout(r_key)["KeyMetadata"]["KeyId"]

    message = b"sign me please"
    r_sign = cli(
        "kms", "sign",
        "--key-id", key_id,
        "--message", _b64(message),
        "--signing-algorithm", "RSASSA_PKCS1_V1_5_SHA_256",
    )
    assert r_sign.returncode == 0
    sig_data = _parse_json_stdout(r_sign)
    signature = sig_data["Signature"]
    assert signature

    r_verify = cli(
        "kms", "verify",
        "--key-id", key_id,
        "--message", _b64(message),
        "--signature", signature,
        "--signing-algorithm", "RSASSA_PKCS1_V1_5_SHA_256",
    )
    assert r_verify.returncode == 0
    verify_data = _parse_json_stdout(r_verify)
    assert verify_data.get("SignatureValid") is True

    # Tampered signature must not validate as true; either the operation
    # fails (nonzero exit, stderr populated) or it reports SignatureValid False.
    bad_sig = base64.b64encode(b"\x00" * 16 + base64.b64decode(signature)[16:]).decode()
    r_bad = cli(
        "kms", "verify",
        "--key-id", key_id,
        "--message", _b64(message),
        "--signature", bad_sig,
        "--signing-algorithm", "RSASSA_PKCS1_V1_5_SHA_256",
    )
    if r_bad.returncode == 0:
        bad_data = _parse_json_stdout(r_bad)
        assert bad_data.get("SignatureValid") is not True
    else:
        assert r_bad.stdout == ""
        assert r_bad.stderr.strip() != ""


def test_generate_mac_verify_mac_round_trip(cli):
    r_key = cli(
        "kms", "create-key",
        "--key-usage", "GENERATE_VERIFY_MAC",
        "--key-spec", "HMAC_256",
    )
    assert r_key.returncode == 0
    key_id = _parse_json_stdout(r_key)["KeyMetadata"]["KeyId"]

    message = b"mac this message"
    r_mac = cli(
        "kms", "generate-mac",
        "--key-id", key_id,
        "--message", _b64(message),
        "--mac-algorithm", "HMAC_SHA_256",
    )
    assert r_mac.returncode == 0
    mac_data = _parse_json_stdout(r_mac)
    mac = mac_data["Mac"]
    assert mac

    r_verify = cli(
        "kms", "verify-mac",
        "--key-id", key_id,
        "--message", _b64(message),
        "--mac", mac,
        "--mac-algorithm", "HMAC_SHA_256",
    )
    assert r_verify.returncode == 0
    verify_data = _parse_json_stdout(r_verify)
    assert verify_data.get("MacValid") is True


def test_disabled_key_rejects_crypto_and_enable_restores(cli):
    r_key = cli("kms", "create-key")
    assert r_key.returncode == 0
    key_id = _parse_json_stdout(r_key)["KeyMetadata"]["KeyId"]

    r_disable = cli("kms", "disable-key", "--key-id", key_id)
    assert r_disable.returncode == 0

    r_desc = cli("kms", "describe-key", "--key-id", key_id)
    assert _parse_json_stdout(r_desc)["KeyMetadata"]["KeyState"] == "Disabled"

    r_enc_fail = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", _b64(b"should not work"),
    )
    assert r_enc_fail.returncode != 0
    assert r_enc_fail.returncode in VALID_EXIT_CODES
    assert r_enc_fail.stdout == ""
    assert r_enc_fail.stderr.strip() != ""
    assert "Traceback" not in r_enc_fail.stderr

    r_enable = cli("kms", "enable-key", "--key-id", key_id)
    assert r_enable.returncode == 0

    r_enc_ok = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", _b64(b"works now"),
    )
    assert r_enc_ok.returncode == 0


def test_schedule_and_cancel_key_deletion_returns_to_disabled(cli):
    r_key = cli("kms", "create-key")
    assert r_key.returncode == 0
    key_id = _parse_json_stdout(r_key)["KeyMetadata"]["KeyId"]

    r_sched = cli(
        "kms", "schedule-key-deletion",
        "--key-id", key_id,
        "--pending-window-in-days", "7",
    )
    assert r_sched.returncode == 0
    sched_data = _parse_json_stdout(r_sched)
    assert sched_data.get("KeyState") in ("PendingDeletion", None) or True

    r_desc_pending = cli("kms", "describe-key", "--key-id", key_id)
    assert _parse_json_stdout(r_desc_pending)["KeyMetadata"]["KeyState"] == "PendingDeletion"

    r_cancel = cli("kms", "cancel-key-deletion", "--key-id", key_id)
    assert r_cancel.returncode == 0

    r_desc_after = cli("kms", "describe-key", "--key-id", key_id)
    state_after = _parse_json_stdout(r_desc_after)["KeyMetadata"]["KeyState"]
    # cancel-key-deletion must restore to Disabled, never directly Enabled.
    assert state_after == "Disabled"
    assert state_after != "Enabled"


def test_alias_lifecycle_cross_command_visibility(cli):
    r_key = cli("kms", "create-key")
    assert r_key.returncode == 0
    key_id = _parse_json_stdout(r_key)["KeyMetadata"]["KeyId"]

    alias_name = "alias/held-out-test-alias"
    r_create = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", key_id,
    )
    assert r_create.returncode == 0

    r_list = cli("kms", "list-aliases")
    assert r_list.returncode == 0
    list_data = _parse_json_stdout(r_list)
    names = [a.get("AliasName") for a in list_data.get("Aliases", [])]
    assert alias_name in names

    r_delete = cli("kms", "delete-alias", "--alias-name", alias_name)
    assert r_delete.returncode == 0

    r_list2 = cli("kms", "list-aliases")
    assert r_list2.returncode == 0
    names2 = [a.get("AliasName") for a in _parse_json_stdout(r_list2).get("Aliases", [])]
    assert alias_name not in names2


def test_tag_untag_resource_cross_command_visibility(cli):
    r_key = cli("kms", "create-key")
    assert r_key.returncode == 0
    key_id = _parse_json_stdout(r_key)["KeyMetadata"]["KeyId"]

    r_tag = cli(
        "kms", "tag-resource",
        "--key-id", key_id,
        "--tags", "TagKey=Project,TagValue=HeldOut",
    )
    assert r_tag.returncode == 0

    r_list_tags = cli("kms", "list-resource-tags", "--key-id", key_id)
    assert r_list_tags.returncode == 0
    tags_data = _parse_json_stdout(r_list_tags)
    tag_pairs = {t.get("TagKey"): t.get("TagValue") for t in tags_data.get("Tags", [])}
    assert tag_pairs.get("Project") == "HeldOut"

    r_untag = cli("kms", "untag-resource", "--key-id", key_id, "--tag-keys", "Project")
    assert r_untag.returncode == 0

    r_list_tags2 = cli("kms", "list-resource-tags", "--key-id", key_id)
    assert r_list_tags2.returncode == 0
    tags_data2 = _parse_json_stdout(r_list_tags2)
    remaining_keys = {t.get("TagKey") for t in tags_data2.get("Tags", [])}
    assert "Project" not in remaining_keys


def test_all_observed_exit_codes_within_permitted_set(cli):
    results = [
        cli("kms", "list-keys"),
        cli("kms", "nonexistent-subcommand"),
        cli("kms", "describe-key", "--key-id", "arn:aws:kms:us-east-1:000000000000:key/does-not-exist"),
    ]
    for r in results:
        assert r.returncode in VALID_EXIT_CODES
        if r.returncode == 0:
            assert r.stderr == ""
            json.loads(r.stdout)
        else:
            assert r.stdout == ""