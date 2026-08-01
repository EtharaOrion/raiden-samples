def test_generate_data_key_without_plaintext_aes_256(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "generate-data-key-without-plaintext test key",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "generate-data-key-without-plaintext",
        "--key-id",
        key_id,
        "--key-spec",
        "AES_256",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert "Plaintext" not in output
    assert isinstance(output["CiphertextBlob"], str)
    assert output["CiphertextBlob"]

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert len(base64.b64decode(decrypted["Plaintext"], validate=True)) == 32
    assert kms.rpc("DescribeKey", {"KeyId": decrypted["KeyId"]})["KeyMetadata"]["KeyId"] == key_id