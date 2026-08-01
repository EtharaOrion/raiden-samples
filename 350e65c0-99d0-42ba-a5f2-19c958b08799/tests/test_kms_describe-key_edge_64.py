def test_describe_key_by_alias_edge(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {"Description": "describe-key edge test"})
    key_id = created["KeyMetadata"]["KeyId"]
    key_arn = created["KeyMetadata"]["Arn"]

    alias_name = "alias/describe-edge-" + key_id[:8]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "describe-key", "--key-id", alias_name)
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    meta = out["KeyMetadata"]
    assert meta["KeyId"] == key_id
    assert meta["Arn"] == key_arn

    described = kms.rpc("DescribeKey", {"KeyId": alias_name})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Arn"] == key_arn
    assert described["KeyMetadata"]["Description"] == "describe-key edge test"