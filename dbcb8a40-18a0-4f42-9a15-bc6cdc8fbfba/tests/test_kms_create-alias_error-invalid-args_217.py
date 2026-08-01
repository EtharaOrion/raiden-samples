def test_create_alias_missing_alias_name_fails(cli, kms, tmp_path):
    # Seed a valid target key so only the missing --alias-name causes failure
    created = kms.rpc("CreateKey", {})
    key_id = created["KeyMetadata"]["KeyId"]

    # Run create-alias without the required --alias-name
    result = cli("kms", "create-alias", "--target-key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "alias-name" in result.stderr.lower() or "argument" in result.stderr.lower()

    # Assert no alias was created pointing to this key
    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert all(a.get("TargetKeyId") != key_id for a in aliases)