def test_list_aliases_limit_returns_at_most_one(cli, kms, tmp_path):
    # Seed prerequisite state: create a key and two aliases
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    import uuid
    alias1 = "alias/" + uuid.uuid4().hex
    alias2 = "alias/" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": alias1, "TargetKeyId": key_id})
    kms.rpc("CreateAlias", {"AliasName": alias2, "TargetKeyId": key_id})

    # Run the command under test
    result = cli("kms", "list-aliases", "--limit", "1")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    aliases = payload.get("Aliases", [])
    # --limit 1 means no more than one item returned
    assert len(aliases) <= 1

    # Independent read: the aliases we created must exist in kms state
    listed = kms.rpc("ListAliases", {})
    names = {a["AliasName"] for a in listed["Aliases"]}
    assert alias1 in names
    assert alias2 in names

    # And any returned alias must be a real alias present in full state
    for a in aliases:
        assert a["AliasName"] in names