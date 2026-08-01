def test_describe_key_returns_existing_key_metadata(cli, kms):
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "describe-key happy path",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]
    key_arn = created["KeyMetadata"]["Arn"]

    result = cli("kms", "describe-key", "--key-id", key_id)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["KeyMetadata"]["KeyId"] == key_id
    assert output["KeyMetadata"]["Arn"] == key_arn

    observed = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert observed["KeyId"] == key_id
    assert observed["Arn"] == key_arn
    assert observed["Description"] == "describe-key happy path"
    assert observed["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert observed["Enabled"] is True