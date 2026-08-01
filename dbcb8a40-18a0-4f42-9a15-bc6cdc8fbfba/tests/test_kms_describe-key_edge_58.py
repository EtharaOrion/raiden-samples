def test_describe_key_with_grant_tokens(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "describe-key grant-tokens test"})
    key_id = created["KeyMetadata"]["KeyId"]
    expected_arn = created["KeyMetadata"]["Arn"]

    result = cli(
        "kms", "describe-key",
        "--key-id", key_id,
        "--grant-tokens", "xxxxxxxxxx",
    )
    assert result.returncode == 0, result.stderr

    import json
    out = json.loads(result.stdout)
    meta = out["KeyMetadata"]
    assert meta["KeyId"] == key_id
    assert meta["Arn"] == expected_arn

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Arn"] == expected_arn