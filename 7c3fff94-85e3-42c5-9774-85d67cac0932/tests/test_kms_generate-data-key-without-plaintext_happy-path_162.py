def test_generate_data_key_without_plaintext_happy_path(cli, kms, tmp_path):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "key for generate-data-key-without-plaintext test",
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
    assert output["CiphertextBlob"]
    assert "Plaintext" not in output

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert len(base64.b64decode(decrypted["Plaintext"], validate=True)) == 32

    described = kms.rpc("DescribeKey", {"KeyId": decrypted["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["KeyState"] == "Enabled"