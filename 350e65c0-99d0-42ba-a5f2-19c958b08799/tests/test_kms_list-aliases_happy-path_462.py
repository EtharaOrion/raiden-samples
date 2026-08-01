def test_list_aliases_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "list-aliases test key"})
    key_id = key["KeyMetadata"]["KeyId"]

    import uuid
    alias_name = "alias/list-aliases-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    aliases = payload["Aliases"]
    names = [a["AliasName"] for a in aliases]
    assert alias_name in names

    # Independent read via raw kms client
    listed = kms.rpc("ListAliases", {})
    seeded = [a for a in listed["Aliases"] if a["AliasName"] == alias_name]
    assert len(seeded) == 1
    assert seeded[0].get("TargetKeyId") == key_id