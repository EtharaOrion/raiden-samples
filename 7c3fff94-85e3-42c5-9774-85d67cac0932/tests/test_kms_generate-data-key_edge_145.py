def test_generate_data_key_aes_256_round_trip(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "generate-data-key AES_256 test",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    metadata = created["KeyMetadata"]
    key_id = metadata["KeyId"]
    key_arn = metadata["Arn"]

    result = cli(
        "kms",
        "generate-data-key",
        "--key-id",
        key_arn,
        "--key-spec",
        "AES_256",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["KeyId"] in (key_id, key_arn)
    assert len(base64.b64decode(output["Plaintext"], validate=True)) == 32
    assert base64.b64decode(output["CiphertextBlob"], validate=True)

    decrypted = kms.rpc(
        "Decrypt",
        {"CiphertextBlob": output["CiphertextBlob"]},
    )
    assert decrypted["KeyId"] in (key_id, key_arn)
    assert decrypted["Plaintext"] == output["Plaintext"]