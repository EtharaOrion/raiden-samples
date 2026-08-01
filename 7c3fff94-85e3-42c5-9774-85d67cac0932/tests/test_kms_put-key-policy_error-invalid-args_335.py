def test_put_key_policy_rejects_empty_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "empty-key-id-policy-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    original_policy = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )["Policy"]

    result = cli(
        "kms",
        "put-key-policy",
        "--key-id",
        "",
        "--policy",
        '{"Version":"2012-10-17","Statement":[]}',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation" in result.stderr

    current_policy = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )["Policy"]
    assert current_policy == original_policy