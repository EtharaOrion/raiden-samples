def test_put_key_policy_missing_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "missing-key-id validation"})
    key_id = created["KeyMetadata"]["KeyId"]

    policy_before = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )["Policy"]

    result = cli("kms", "put-key-policy", "--policy", "{}")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    policy_after = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )["Policy"]
    assert policy_after == policy_before