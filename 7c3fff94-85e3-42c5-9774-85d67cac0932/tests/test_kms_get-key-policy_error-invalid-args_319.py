def test_get_key_policy_rejects_empty_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "empty-key-id validation sentinel"})
    key_metadata = created["KeyMetadata"]
    key_id = key_metadata["KeyId"]

    result = cli("kms", "get-key-policy", "--key-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr
    assert "KeyId" in result.stderr

    described = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert described["KeyId"] == key_id
    assert described["Description"] == "empty-key-id validation sentinel"
    assert described["Enabled"] is True