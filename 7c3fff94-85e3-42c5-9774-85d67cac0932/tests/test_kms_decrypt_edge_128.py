def test_decrypt_valid_ciphertext_blob_edge(cli, kms, tmp_path):
    import base64
    import json

    plaintext = b"decrypt edge-case plaintext"
    created = kms.rpc("CreateKey", {"Description": "decrypt edge test"})
    key_id = created["KeyMetadata"]["KeyId"]

    encrypted = kms.rpc(
        "Encrypt",
        {
            "KeyId": key_id,
            "Plaintext": base64.b64encode(plaintext).decode("ascii"),
        },
    )

    blob_path = tmp_path / "x"
    blob_path.write_bytes(base64.b64decode(encrypted["CiphertextBlob"]))

    result = cli(
        "kms",
        "decrypt",
        "--ciphertext-blob",
        f"fileb://{blob_path}",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert base64.b64decode(output["Plaintext"]) == plaintext

    independently_decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": encrypted["CiphertextBlob"]},
    )
    assert base64.b64decode(independently_decrypted["Plaintext"]) == plaintext
    assert independently_decrypted["KeyId"] == encrypted["KeyId"]