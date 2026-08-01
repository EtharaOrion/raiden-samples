"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

import json
import pytest


def _create_key(cli):
    r = cli("kms", "create-key")
    assert r.returncode == 0, r.stderr
    body = json.loads(r.stdout)
    return body["KeyMetadata"]["KeyId"]


def test_unknown_subcommand_is_usage_error(cli):
    r = cli("kms", "not-a-real-subcommand")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_missing_kms_group_is_usage_error(cli):
    r = cli("ec2", "describe-instances")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_no_args_is_usage_error(cli):
    r = cli()
    assert r.returncode != 0
    assert r.stdout == ""


def test_create_key_visible_in_list_and_describe(cli):
    key_id = _create_key(cli)

    r_list = cli("kms", "list-keys")
    assert r_list.returncode == 0
    listed = json.loads(r_list.stdout)
    ids = [k["KeyId"] for k in listed.get("Keys", [])]
    assert key_id in ids

    r_desc = cli("kms", "describe-key", "--key-id", key_id)
    assert r_desc.returncode == 0
    desc = json.loads(r_desc.stdout)
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["KeyState"] == "Enabled"


def test_encrypt_decrypt_roundtrip(cli):
    key_id = _create_key(cli)
    plaintext = "aGVsbG8gd29ybGQ="  # base64 "hello world"

    r_enc = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)
    assert r_enc.returncode == 0, r_enc.stderr
    enc = json.loads(r_enc.stdout)
    ciphertext = enc["CiphertextBlob"]
    assert ciphertext

    r_dec = cli("kms", "decrypt", "--ciphertext-blob", ciphertext)
    assert r_dec.returncode == 0, r_dec.stderr
    dec = json.loads(r_dec.stdout)
    assert dec["Plaintext"] == plaintext


def test_alias_usable_as_key_id(cli):
    key_id = _create_key(cli)
    alias_name = "alias/test-alias-r2e"

    r_alias = cli("kms", "create-alias", "--alias-name", alias_name, "--target-key-id", key_id)
    assert r_alias.returncode == 0, r_alias.stderr
    assert r_alias.stderr == ""

    r_list = cli("kms", "list-aliases")
    assert r_list.returncode == 0
    aliases = json.loads(r_list.stdout).get("Aliases", [])
    names = [a["AliasName"] for a in aliases]
    assert alias_name in names

    r_desc = cli("kms", "describe-key", "--key-id", alias_name)
    assert r_desc.returncode == 0, r_desc.stderr
    desc = json.loads(r_desc.stdout)
    assert desc["KeyMetadata"]["KeyId"] == key_id


def test_disable_enable_reflected_in_describe(cli):
    key_id = _create_key(cli)

    r_dis = cli("kms", "disable-key", "--key-id", key_id)
    assert r_dis.returncode == 0, r_dis.stderr

    r_desc1 = cli("kms", "describe-key", "--key-id", key_id)
    assert r_desc1.returncode == 0
    assert json.loads(r_desc1.stdout)["KeyMetadata"]["KeyState"] == "Disabled"

    r_en = cli("kms", "enable-key", "--key-id", key_id)
    assert r_en.returncode == 0, r_en.stderr

    r_desc2 = cli("kms", "describe-key", "--key-id", key_id)
    assert r_desc2.returncode == 0
    assert json.loads(r_desc2.stdout)["KeyMetadata"]["KeyState"] == "Enabled"


def test_generate_data_key_roundtrip(cli):
    key_id = _create_key(cli)

    r_gen = cli("kms", "generate-data-key", "--key-id", key_id, "--number-of-bytes", "32")
    assert r_gen.returncode == 0, r_gen.stderr
    gen = json.loads(r_gen.stdout)
    assert "Plaintext" in gen
    assert "CiphertextBlob" in gen

    r_dec = cli("kms", "decrypt", "--ciphertext-blob", gen["CiphertextBlob"])
    assert r_dec.returncode == 0, r_dec.stderr
    dec = json.loads(r_dec.stdout)
    assert dec["Plaintext"] == gen["Plaintext"]


def test_duplicate_flag_is_usage_error(cli):
    r = cli("kms", "create-key", "--description", "a", "--description", "b")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_missing_required_flag_is_usage_error(cli):
    r = cli("kms", "describe-key")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_out_of_range_limit_is_usage_error(cli):
    r = cli("kms", "list-keys", "--limit", "5000")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_oversized_alias_name_is_usage_error(cli):
    huge_alias = "alias/" + ("x" * 300)
    r = cli("kms", "create-alias", "--alias-name", huge_alias, "--target-key-id", "1234")
    assert r.returncode == 252
    assert r.stdout == ""


def test_nonexistent_key_id_is_service_error(cli):
    r = cli("kms", "describe-key", "--key-id", "00000000-0000-0000-0000-000000000000")
    assert r.returncode in (254, 255, 1)
    assert r.returncode != 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_all_exit_codes_within_allowed_set(cli):
    allowed = {0, 1, 252, 254, 255}
    scenarios = [
        cli("kms", "list-keys"),
        cli("kms", "bogus-subcommand"),
        cli("kms", "describe-key", "--key-id", "nonexistent-key-xyz"),
        cli("kms", "create-key", "--unknown-flag", "x"),
    ]
    for r in scenarios:
        assert r.returncode in allowed
        if r.returncode != 0:
            assert r.stdout == ""