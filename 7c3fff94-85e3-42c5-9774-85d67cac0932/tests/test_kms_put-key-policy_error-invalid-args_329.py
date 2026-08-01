def test_put_key_policy_missing_required_policy(cli, kms):
    import json

    created = kms.rpc("CreateKey", {"Description": "missing-policy-argument-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )
    before_policy = json.loads(before["Policy"])

    result = cli("kms", "put-key-policy", "--key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--policy" in result.stderr

    after = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )
    assert json.loads(after["Policy"]) == before_policy