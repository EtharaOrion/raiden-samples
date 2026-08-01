def test_encrypt_invalid_args_unknown_flag(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {"Description": "enc-invalid-args"})
    key_id = key["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", "aGVsbG8=",
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "argument" in result.stderr.lower() or "unknown" in result.stderr.lower() or "usage" in result.stderr.lower()

    # Key remains intact and usable via a proper round trip
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["Enabled"] is True

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": "aGVsbG8="})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert dec["Plaintext"] == "aGVsbG8="