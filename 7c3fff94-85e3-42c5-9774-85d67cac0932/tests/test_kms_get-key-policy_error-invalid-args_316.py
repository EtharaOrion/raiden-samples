def test_get_key_policy_rejects_unknown_flag_without_changing_policy(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "invalid-argument policy test"})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )
    assert isinstance(before["Policy"], str)
    assert before["Policy"]

    result = cli(
        "kms",
        "get-key-policy",
        "--key-id",
        key_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )
    assert after["Policy"] == before["Policy"]