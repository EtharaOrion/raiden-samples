def test_list_aliases_invalid_marker_edge(cli, kms):
    # Seed a key and alias so aliases exist in the account/region
    created = kms.rpc("CreateKey", {"Description": "list-aliases marker edge"})
    key_id = created["KeyMetadata"]["KeyId"]
    alias_name = "alias/marker-edge-" + key_id[:8]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    # An oversized/opaque marker value is rejected by the service
    bad_marker = "x" * 320
    result = cli("kms", "list-aliases", "--marker", bad_marker)

    assert result.returncode != 0
    assert "InvalidMarker" in result.stderr

    # State assertion: the alias we created is still present (unaffected)
    aliases = kms.rpc("ListAliases", {})["Aliases"]
    names = {a["AliasName"] for a in aliases}
    assert alias_name in names