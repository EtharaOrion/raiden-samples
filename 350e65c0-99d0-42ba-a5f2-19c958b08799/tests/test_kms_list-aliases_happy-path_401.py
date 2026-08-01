def test_list_aliases_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "list-aliases-test"})
    key_id = key["KeyMetadata"]["KeyId"]

    import uuid
    alias_name = "alias/list-aliases-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    aliases = payload["Aliases"]
    names = {a["AliasName"] for a in aliases}
    assert alias_name in names

    match = [a for a in aliases if a["AliasName"] == alias_name][0]
    assert match.get("TargetKeyId") == key_id

    # independent read-back via kms
    server_aliases = kms.rpc("ListAliases", {})["Aliases"]
    server_names = {a["AliasName"] for a in server_aliases}
    assert alias_name in server_names