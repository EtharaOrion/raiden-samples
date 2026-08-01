def test_list_aliases_limit_pagination(cli, kms, tmp_path):
    # Seed prerequisite state: create a key and two aliases so at least one alias exists
    key = kms.rpc("CreateKey", {"Description": "list-aliases-limit test"})
    key_id = key["KeyMetadata"]["KeyId"]

    import uuid
    name_a = "alias/list-limit-a-" + uuid.uuid4().hex
    name_b = "alias/list-limit-b-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": name_a, "TargetKeyId": key_id})
    kms.rpc("CreateAlias", {"AliasName": name_b, "TargetKeyId": key_id})

    # Run command under test with --limit 1
    result = cli("kms", "list-aliases", "--limit", "1")
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    assert "Aliases" in out
    assert isinstance(out["Aliases"], list)
    # With limit 1, at most one alias should be returned in this page
    assert len(out["Aliases"]) <= 1

    # Independent read: the seeded aliases exist in full listing
    all_aliases = kms.rpc("ListAliases", {})
    names = {a["AliasName"] for a in all_aliases["Aliases"]}
    assert name_a in names
    assert name_b in names