def test_kms_decrypt_round_trip(cli, kms, tmp_path):
    import base64
    import json

    # Seed: create a symmetric key
    create = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt some plaintext to produce a ciphertext blob
    plaintext = b"hello-decrypt-round-trip"
    plaintext_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    # Write ciphertext bytes to a file so the CLI can read it as a blob
    blob_path = tmp_path / "ciphertext.bin"
    blob_path.write_bytes(base64.b64decode(ciphertext_b64))

    # Run the command under test
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{blob_path}",
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # Assert the CLI returned the correct key and decrypted plaintext
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id
    returned_plaintext = base64.b64decode(out["Plaintext"])
    assert returned_plaintext == plaintext

    # Independent state assertion: decrypt via raw RPC yields original plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id