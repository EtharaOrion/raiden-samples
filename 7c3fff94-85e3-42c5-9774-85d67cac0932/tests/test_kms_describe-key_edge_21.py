def test_describe_key_with_grant_token(cli, kms):
    import json

    created = kms.rpc(
        "CreateKey",
        {"Description": "describe-key grant-token edge test"},
    )
    key_metadata = created["KeyMetadata"]
    key_id = key_metadata["KeyId"]
    key_arn = key_metadata["Arn"]

    result = cli(
        "kms",
        "describe-key",
        "--key-id",
        key_id,
        "--grant-tokens",
        "xxxxxxxxxx",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["KeyMetadata"]["KeyId"] == key_id
    assert output["KeyMetadata"]["Arn"] == key_arn

    observed = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert observed["KeyId"] == key_id
    assert observed["Arn"] == key_arn
    assert observed["Description"] == "describe-key grant-token edge test"