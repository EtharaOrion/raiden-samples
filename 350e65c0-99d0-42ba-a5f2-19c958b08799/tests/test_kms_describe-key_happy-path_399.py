def test_describe_key_happy_path(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {"Description": "describe-key happy path"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "describe-key", "--key-id", key_id)
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    assert out["KeyMetadata"]["KeyId"] == key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Description"] == "describe-key happy path"