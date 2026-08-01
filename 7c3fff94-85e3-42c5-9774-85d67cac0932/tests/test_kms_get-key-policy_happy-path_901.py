def test_get_key_policy_happy_path_default_matches_backend(cli, kms):
    import json
    import uuid

    created = kms.rpc(
        "CreateKey",
        {"Description": "get-key-policy-happy-" + uuid.uuid4().hex},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "get-key-policy",
        "--key-id",
        key_id,
        "--policy-name",
        "default",
    )
    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    assert isinstance(output["Policy"], str)
    assert output["Policy"]

    stored = kms.rpc(
        "GetKeyPolicy",
        {"KeyId": key_id, "PolicyName": "default"},
    )
    assert json.loads(output["Policy"]) == json.loads(stored["Policy"])
