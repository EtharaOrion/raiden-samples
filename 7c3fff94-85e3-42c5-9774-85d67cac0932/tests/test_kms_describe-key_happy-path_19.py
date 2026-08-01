def test_describe_key_existing_key(cli, kms):
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

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["KeyMetadata"]["KeyId"] == key_id
    assert output["KeyMetadata"]["Arn"] == key_arn
    assert output["KeyMetadata"]["KeyUsage"] == "ENCRYPT_DECRYPT"

    observed = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert observed["KeyId"] == key_id
    assert observed["Arn"] == key_arn
    assert observed["Description"] == "describe-key happy path"
    assert observed["Enabled"] is True
    assert observed["KeyState"] == "Enabled"