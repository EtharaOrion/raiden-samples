def test_re_encrypt_changes_protecting_key_and_preserves_plaintext(cli, kms, tmp_path):
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

    plaintext = b"plaintext preserved across re-encryption"
    encrypted = kms.rpc("Encrypt", {
        "KeyId": source_key["KeyId"],
        "Plaintext": base64.b64encode(plaintext).decode("ascii"),
    })

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
    assert isinstance(output["CiphertextBlob"], str)
    assert output["KeyId"] in {
        destination_key["KeyId"],
        destination_key["Arn"],
    }

    decrypted = kms.rpc("Decrypt", {
        "CiphertextBlob": output["CiphertextBlob"],
    })
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"] in {
        destination_key["KeyId"],
        destination_key["Arn"],
    }