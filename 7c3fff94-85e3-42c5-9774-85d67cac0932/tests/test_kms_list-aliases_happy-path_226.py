def test_list_aliases_happy_path(cli, kms):
    import json
    import uuid

    key = kms.rpc("CreateKey", {
        "Description": "Key for list-aliases test",
    })
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = f"alias/list-aliases-{uuid.uuid4().hex}"
    kms.rpc("CreateAlias", {
        "AliasName": alias_name,
        "TargetKeyId": key_id,
    })

    result = cli("kms", "list-aliases")

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert isinstance(output["Aliases"], list)
    assert any(
        alias.get("AliasName") == alias_name
        and alias.get("TargetKeyId") == key_id
        for alias in output["Aliases"]
    )

    state = kms.rpc("ListAliases", {})
    assert any(
        alias.get("AliasName") == alias_name
        and alias.get("TargetKeyId") == key_id
        for alias in state["Aliases"]
    )