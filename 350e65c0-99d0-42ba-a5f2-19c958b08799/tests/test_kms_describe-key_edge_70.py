def test_describe_key_with_grant_tokens(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {"Description": "describe-key-grant-tokens"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "describe-key",
        "--key-id", key_id,
        "--grant-tokens", "xxxxxxxxxx",
    )
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    assert out["KeyMetadata"]["KeyId"] == key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Description"] == "describe-key-grant-tokens"