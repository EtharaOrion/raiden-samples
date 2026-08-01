def test_decrypt_round_trip_recovers_plaintext(cli, kms, tmp_path):
    import base64, json

    key = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-payload"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    blob_path = tmp_path / "cipher.bin"
    blob_path.write_bytes(base64.b64decode(ciphertext_b64))

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", "fileb://" + str(blob_path),
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # Independent verification via raw RPC round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id