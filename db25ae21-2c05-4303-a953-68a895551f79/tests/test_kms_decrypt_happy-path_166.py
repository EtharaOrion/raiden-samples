def test_decrypt_round_trip_happy_path(cli, kms):
    import base64, json

    # Seed: create a symmetric encryption key
    create = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext to obtain ciphertext
    plaintext = b"hello decrypt world"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Run the command under test: decrypt the ciphertext
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_blob,
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)

    # The decrypted plaintext must round-trip to the original input
    returned_pt = base64.b64decode(out["Plaintext"])
    assert returned_pt == plaintext

    # Independent read: the key used must be the one we created
    described = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id

    # Cross-check via the raw kms decrypt too
    verify = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(verify["Plaintext"]) == plaintext
    assert verify["KeyId"].endswith(key_id) or verify["KeyId"] == key_id