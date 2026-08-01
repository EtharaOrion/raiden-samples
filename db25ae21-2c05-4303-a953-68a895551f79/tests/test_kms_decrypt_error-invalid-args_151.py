def test_kms_decrypt_disabled_key_error(cli, kms, tmp_path):
    import base64, json

    # Seed: create a key and encrypt plaintext under it
    create = kms.rpc("CreateKey", {})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = base64.b64encode(b"secret-data").decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext})
    ciphertext_blob = enc["CiphertextBlob"]

    # Disable the key so Decrypt should fail
    kms.rpc("DisableKey", {"KeyId": key_id})
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["Enabled"] is False

    # aws cli reads blob from file:// or as fileb; pass base64-decoded bytes via file
    blob_file = tmp_path / "blob.bin"
    blob_file.write_bytes(base64.b64decode(ciphertext_blob))

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{blob_file}",
        "--key-id", key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "DisabledException" in result.stderr

    # Key still describable and remains disabled
    desc2 = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc2["KeyMetadata"]["Enabled"] is False