def test_re_encrypt_rewraps_ciphertext_with_destination_key(cli, kms, tmp_path):
    import base64
    import json

    source_key = kms.rpc(
        "CreateKey",
        {"Description": "re-encrypt test source key"},
    )["KeyMetadata"]
    destination_key = kms.rpc(
        "CreateKey",
        {"Description": "re-encrypt test destination key"},
    )["KeyMetadata"]

    plaintext = b"plaintext protected by a replacement KMS key"
    encrypted = kms.rpc(
        "Encrypt",
        {
            "KeyId": source_key["KeyId"],
            "Plaintext": base64.b64encode(plaintext).decode("ascii"),
        },
    )

    ciphertext_file = tmp_path / "source-ciphertext.bin"
    ciphertext_file.write_bytes(base64.b64decode(encrypted["CiphertextBlob"]))

    result = cli(
        "kms",
        "re-encrypt",
        "--ciphertext-blob",
        f"fileb://{ciphertext_file}",
        "--destination-key-id",
        destination_key["KeyId"],
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["KeyId"] == destination_key["Arn"]
    assert isinstance(output["CiphertextBlob"], str)
    assert output["CiphertextBlob"]

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert decrypted["KeyId"] == destination_key["Arn"]
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext