def test_list_aliases_shows_created_alias(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "list-aliases test"})
    key_id = key["KeyMetadata"]["KeyId"]

    import uuid
    alias_name = "alias/list-aliases-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    aliases = parsed["Aliases"]
    names = [a["AliasName"] for a in aliases]
    assert alias_name in names

    entry = next(a for a in aliases if a["AliasName"] == alias_name)
    assert entry.get("TargetKeyId") == key_id

    # Independent state assertion via the raw RPC
    listed = kms.rpc("ListAliases", {})
    listed_names = [a["AliasName"] for a in listed["Aliases"]]
    assert alias_name in listed_names