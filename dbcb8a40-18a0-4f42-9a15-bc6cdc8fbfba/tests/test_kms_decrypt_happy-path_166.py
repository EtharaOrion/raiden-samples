def test_kms_decrypt_round_trip(cli, kms, tmp_path):
    import base64, json

    # Prerequisite: create a symmetric key and encrypt a known plaintext.
    key = kms.rpc("CreateKey", {"Description": "decrypt happy path"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top secret message"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    # Run the command under test: decrypt the ciphertext.
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_b64,
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # Decrypt returns Plaintext base64-encoded; must match original.
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert key_id in out["KeyId"]

    # Independent read-back: decrypt via raw RPC and confirm round trip.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext