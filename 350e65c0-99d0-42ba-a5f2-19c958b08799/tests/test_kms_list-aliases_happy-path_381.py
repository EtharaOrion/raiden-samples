def test_list_aliases_happy_path(cli, kms):
    key_id = kms.rpc("CreateKey", {})["KeyMetadata"]["KeyId"]
    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex[:12]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    aliases = payload["Aliases"]
    matching = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(matching) == 1
    assert matching[0].get("TargetKeyId") == key_id

    # confirm via independent read through kms
    backend = kms.rpc("ListAliases", {})["Aliases"]
    backend_match = [a for a in backend if a["AliasName"] == alias_name]
    assert len(backend_match) == 1
    assert backend_match[0].get("TargetKeyId") == key_id