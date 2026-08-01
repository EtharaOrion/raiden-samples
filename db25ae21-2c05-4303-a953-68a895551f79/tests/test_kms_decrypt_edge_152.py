def test_decrypt_with_grant_tokens_roundtrip(cli, kms, tmp_path):
    import base64, json

    # Seed: create a symmetric key
    create = kms.rpc("CreateKey", {"Description": "decrypt-grant-tokens-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext to produce a valid ciphertext blob
    plaintext = b"hello-grant-token-decrypt"
    plaintext_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Write ciphertext blob to a file so the CLI reads raw bytes via fileb://
    blob_path = tmp_path / "ciphertext.blob"
    blob_path.write_bytes(base64.b64decode(ciphertext_blob))

    # Run the command under test with grant tokens
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{blob_path}",
        "--grant-tokens", "xxxxxxxxxx",
    )

    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # Round-trip: decrypted plaintext must equal the original input
    assert base64.b64decode(out["Plaintext"]) == plaintext
    # The reported KeyId must resolve to our seeded key
    described = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id