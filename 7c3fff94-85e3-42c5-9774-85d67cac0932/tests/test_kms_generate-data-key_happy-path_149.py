def test_generate_data_key_happy_path(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "generate-data-key happy path",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "generate-data-key",
        "--key-id",
        key_id,
        "--key-spec",
        "AES_256",
    )
    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    assert output["KeyId"]
    assert output["Plaintext"]
    assert output["CiphertextBlob"]
    assert len(base64.b64decode(output["Plaintext"])) == 32

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert base64.b64decode(decrypted["Plaintext"]) == base64.b64decode(
        output["Plaintext"]
    )

    described = kms.rpc("DescribeKey", {"KeyId": output["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert decrypted["KeyId"] in (key_id, described["KeyMetadata"]["Arn"])