def test_create_alias_empty_alias_name(cli, kms):
    create = kms.rpc("CreateKey", {})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli("kms", "create-alias", "--alias-name", "", "--target-key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "Invalid" in result.stderr

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    for a in aliases:
        assert a.get("AliasName") != ""
        assert a.get("AliasName") != "alias/"