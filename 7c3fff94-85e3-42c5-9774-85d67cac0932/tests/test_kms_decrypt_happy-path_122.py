def test_decrypt_happy_path(cli, kms, tmp_path):
    import base64
    import json

    plaintext = b"black-box decrypt round trip"

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "decrypt happy path",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    encrypted = kms.rpc(
        "Encrypt",
        {
            "KeyId": key_id,
            "Plaintext": base64.b64encode(plaintext).decode("ascii"),
        },
    )

    ciphertext_path = tmp_path / "ciphertext.bin"
    ciphertext_path.write_bytes(
        base64.b64decode(encrypted["CiphertextBlob"], validate=True)
    )

    result = cli(
        "kms",
        "decrypt",
        "--ciphertext-blob",
        f"fileb://{ciphertext_path}",
        "--key-id",
        key_id,
        "--output",
        "json",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert base64.b64decode(output["Plaintext"], validate=True) == plaintext
    assert output["KeyId"]

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"

    independently_decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": encrypted["CiphertextBlob"]},
    )
    assert (
        base64.b64decode(independently_decrypted["Plaintext"], validate=True)
        == plaintext
    )