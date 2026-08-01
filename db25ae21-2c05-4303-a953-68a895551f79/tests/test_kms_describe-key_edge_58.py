def test_describe_key_with_grant_tokens(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "grant-token-describe-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    key_arn = created["KeyMetadata"]["Arn"]

    result = cli(
        "kms", "describe-key",
        "--key-id", key_id,
        "--grant-tokens", "xxxxxxxxxx",
    )
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    assert out["KeyMetadata"]["KeyId"] == key_id
    assert out["KeyMetadata"]["Arn"] == key_arn

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Arn"] == key_arn