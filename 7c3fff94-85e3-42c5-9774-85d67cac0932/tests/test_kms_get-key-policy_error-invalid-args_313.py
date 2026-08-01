def test_get_key_policy_missing_required_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "key for missing get-key-policy argument test"},
    )
    key_id = created["KeyMetadata"]["KeyId"]
    original_policy = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )["Policy"]

    result = cli("kms", "get-key-policy")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    policy_after = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )["Policy"]
    assert policy_after == original_policy