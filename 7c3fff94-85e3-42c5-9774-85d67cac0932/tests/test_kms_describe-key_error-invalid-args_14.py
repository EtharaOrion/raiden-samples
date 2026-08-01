def test_describe_key_missing_required_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "describe-key invalid-args state sentinel"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "describe-key")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == "describe-key invalid-args state sentinel"
    assert metadata["KeyState"] == "Enabled"