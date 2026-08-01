def test_describe_key_existing_key(cli, kms, tmp_path):
    import json

    created = kms.rpc(
        "CreateKey",
        {"Description": "key for describe-key happy-path test"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "describe-key", "--key-id", key_id)

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["KeyMetadata"]["KeyId"] == key_id
    assert output["KeyMetadata"]["Description"] == "key for describe-key happy-path test"

    observed = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert observed["KeyId"] == key_id
    assert observed["Description"] == "key for describe-key happy-path test"
    assert observed["KeyState"] == "Enabled"