def test_create_alias_invalid_alias_name(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    long_alias = "alias/" + "x" * 500

    result = cli("kms", "create-alias",
                 "--alias-name", long_alias,
                 "--target-key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidAliasName" in result.stderr or "ValidationException" in result.stderr or "InvalidAliasNameException" in result.stderr

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert all(a.get("AliasName") != long_alias for a in aliases)