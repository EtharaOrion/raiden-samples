def test_re_encrypt_rewraps_ciphertext_under_destination_key(cli, kms, tmp_path):
    import base64
    import json

    source_key = kms.rpc("CreateKey", {
        "Description": "re-encrypt source key",
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "SYMMETRIC_DEFAULT",
    })["KeyMetadata"]
    destination_key = kms.rpc("CreateKey", {
        "Description": "re-encrypt destination key",
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "SYMMETRIC_DEFAULT",
    })["KeyMetadata"]

    plaintext = b"plaintext to re-encrypt under a different KMS key"
    encrypted = kms.rpc("Encrypt", {
        "KeyId": source_key["KeyId"],
        "Plaintext": base64.b64encode(plaintext).decode("ascii"),
    })

    ciphertext_path = tmp_path / "source-ciphertext.bin"
    ciphertext_path.write_bytes(base64.b64decode(encrypted["CiphertextBlob"]))

    result = cli(
        "kms",
        "re-encrypt",
        "--ciphertext-blob",
        f"fileb://{ciphertext_path}",
        "--destination-key-id",
        destination_key["KeyId"],
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert isinstance(output["CiphertextBlob"], str)
    assert output["CiphertextBlob"] != encrypted["CiphertextBlob"]

    decrypted = kms.rpc("Decrypt", {
        "CiphertextBlob": output["CiphertextBlob"],
    })
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"] in {
        destination_key["KeyId"],
        destination_key["Arn"],
    }