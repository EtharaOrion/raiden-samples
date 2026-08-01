def test_decrypt_round_trip_happy_path(cli, kms, tmp_path):
    import base64, json

    key = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"the quick brown fox"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # aws cli fileb:// reads raw bytes; write decoded ciphertext to a file
    blob_file = tmp_path / "cipher.bin"
    blob_file.write_bytes(base64.b64decode(ciphertext_blob))

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{blob_file}",
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # independent read: decrypt directly against backend, verify round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id)