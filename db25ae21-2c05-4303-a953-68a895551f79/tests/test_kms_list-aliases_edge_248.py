def test_list_aliases_limit_pagination(cli, kms):
    # Seed prerequisite state: create a key and two aliases so there are
    # at least 2 aliases available to page through.
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    import uuid
    name_a = "alias/test-" + uuid.uuid4().hex
    name_b = "alias/test-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": name_a, "TargetKeyId": key_id})
    kms.rpc("CreateAlias", {"AliasName": name_b, "TargetKeyId": key_id})

    # Command under test: list aliases with a limit of 1.
    result = cli("kms", "list-aliases", "--limit", "1")
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    aliases = out.get("Aliases", [])
    # With --limit 1 no more than one alias should be returned.
    assert len(aliases) <= 1
    for a in aliases:
        assert "AliasName" in a

    # Independent read-back through kms: both seeded aliases exist in full listing.
    listed = kms.rpc("ListAliases", {})
    all_names = {a["AliasName"] for a in listed.get("Aliases", [])}
    assert name_a in all_names
    assert name_b in all_names