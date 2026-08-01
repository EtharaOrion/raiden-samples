def test_list_aliases_happy_path(cli, kms):
    key_id = kms.rpc("CreateKey", {})["KeyMetadata"]["KeyId"]
    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    aliases = payload["Aliases"]
    matching = [a for a in aliases if a["AliasName"] == alias_name]
    assert matching, f"{alias_name} not found in list-aliases output"
    assert matching[0].get("TargetKeyId") == key_id

    # Independent verification via kms state
    state_aliases = kms.rpc("ListAliases", {})["Aliases"]
    state_match = [a for a in state_aliases if a["AliasName"] == alias_name]
    assert state_match
    assert state_match[0].get("TargetKeyId") == key_id