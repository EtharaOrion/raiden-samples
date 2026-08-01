def test_describe_key_happy_path(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "describe-key-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "describe-key", "--key-id", key_id)
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    assert parsed["KeyMetadata"]["KeyId"] == key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Description"] == "describe-key-test"