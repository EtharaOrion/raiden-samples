def test_decrypt_disabled_key_fails(cli, kms, tmp_path):
    import base64, json

    # Create a symmetric key
    create = kms.rpc("CreateKey", {})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt some plaintext while key is enabled
    plaintext = base64.b64encode(b"secret-message").decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext})
    ciphertext_blob = enc["CiphertextBlob"]

    # Disable the key
    kms.rpc("DisableKey", {"KeyId": key_id})

    # Confirm the key is disabled in state
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["Enabled"] is False

    # Write the ciphertext blob to a file so the CLI reads it as raw bytes
    blob_file = tmp_path / "blob.bin"
    blob_file.write_bytes(base64.b64decode(ciphertext_blob))

    # Attempt to decrypt with a disabled key -> should fail with DisabledException
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", "fileb://" + str(blob_file),
        "--key-id", key_id,
    )

    assert result.returncode != 0
    assert "DisabledException" in result.stderr

    # Verify state: key still describes as disabled
    desc2 = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc2["KeyMetadata"]["Enabled"] is False