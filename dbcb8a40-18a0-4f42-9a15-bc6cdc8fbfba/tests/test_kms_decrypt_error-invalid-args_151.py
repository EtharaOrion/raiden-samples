def test_decrypt_disabled_key_error(cli, kms, tmp_path):
    import base64, json

    # Seed: create a key, encrypt data under it, then disable the key.
    create = kms.rpc("CreateKey", {"Description": "decrypt-disabled-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = base64.b64encode(b"secret-payload").decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext})
    ciphertext_blob = enc["CiphertextBlob"]

    # Disable the key so Decrypt should fail with DisabledException.
    kms.rpc("DisableKey", {"KeyId": key_id})

    # Confirm the key is indeed disabled before running the command under test.
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["Enabled"] is False

    # aws kms decrypt accepts the ciphertext blob as base64 via fileb:// or a
    # blob value; use a file with the raw bytes for the blob argument.
    blob_bytes = base64.b64decode(ciphertext_blob)
    blob_file = tmp_path / "cipher.blob"
    blob_file.write_bytes(blob_bytes)

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{blob_file}",
        "--key-id", key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "DisabledException" in result.stderr

    # State assertion: key remains present and disabled.
    desc2 = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc2["KeyMetadata"]["Enabled"] is False