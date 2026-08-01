def test_list_aliases_filters_by_key_id(cli, kms, tmp_path):
    import json

    key = kms.rpc("CreateKey", {"Description": "list-aliases filter target"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = "alias/list-aliases-" + key_id

    other_key = kms.rpc("CreateKey", {"Description": "list-aliases non-target"})
    other_key_id = other_key["KeyMetadata"]["KeyId"]
    other_alias_name = "alias/list-aliases-other-" + other_key_id

    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})
    kms.rpc(
        "CreateAlias",
        {"AliasName": other_alias_name, "TargetKeyId": other_key_id},
    )

    result = cli("kms", "list-aliases", "--key-id", key_id)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "Aliases" in output
    assert any(
        alias["AliasName"] == alias_name and alias["TargetKeyId"] == key_id
        for alias in output["Aliases"]
    )
    assert all(
        alias.get("TargetKeyId") == key_id
        for alias in output["Aliases"]
    )
    assert all(
        alias["AliasName"] != other_alias_name
        for alias in output["Aliases"]
    )

    state = kms.rpc("ListAliases", {"KeyId": key_id})
    assert any(
        alias["AliasName"] == alias_name and alias["TargetKeyId"] == key_id
        for alias in state["Aliases"]
    )
    assert all(
        alias.get("TargetKeyId") == key_id
        for alias in state["Aliases"]
    )