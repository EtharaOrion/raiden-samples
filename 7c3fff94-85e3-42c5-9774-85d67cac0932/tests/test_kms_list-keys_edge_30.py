def test_list_keys_with_maximum_limit(cli, kms):
    import json

    created = kms.rpc(
        "CreateKey",
        {"Description": "list-keys maximum-limit test"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "list-keys", "--limit", "1000")

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert isinstance(output["Keys"], list)
    assert any(key["KeyId"] == key_id for key in output["Keys"])

    state = kms.rpc("ListKeys", {"Limit": 1000})
    assert any(key["KeyId"] == key_id for key in state["Keys"])