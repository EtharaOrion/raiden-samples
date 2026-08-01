def test_describe_key_happy_path(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {"Description": "describe-key happy path"})
    key_id = created["KeyMetadata"]["KeyId"]
    expected_arn = created["KeyMetadata"]["Arn"]

    result = cli("kms", "describe-key", "--key-id", key_id)
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    meta = payload["KeyMetadata"]
    assert meta["KeyId"] == key_id
    assert meta["Arn"] == expected_arn

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Arn"] == expected_arn