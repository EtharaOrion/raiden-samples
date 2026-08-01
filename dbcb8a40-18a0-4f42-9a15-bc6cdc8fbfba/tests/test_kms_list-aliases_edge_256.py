def test_list_aliases_with_invalid_marker(cli, kms):
    # Seed prerequisite state: a key and an alias associated with it
    create = kms.rpc("CreateKey", {})
    key_id = create["KeyMetadata"]["KeyId"]
    alias_name = "alias/test-list-aliases-marker-key"
    # Clean any pre-existing alias name collision by using a unique name
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    bogus_marker = "x" * 320

    result = cli("kms", "list-aliases", "--marker", bogus_marker)

    # The marker is syntactically invalid -> the real AWS CLI rejects it.
    assert result.returncode != 0
    assert "InvalidMarkerException" in result.stderr

    # Independent state read: the seeded alias still exists and points at our key.
    aliases = kms.rpc("ListAliases", {})["Aliases"]
    match = [a for a in aliases if a["AliasName"] == alias_name]
    assert match, f"expected alias {alias_name} to be present"
    assert match[0].get("TargetKeyId") == key_id