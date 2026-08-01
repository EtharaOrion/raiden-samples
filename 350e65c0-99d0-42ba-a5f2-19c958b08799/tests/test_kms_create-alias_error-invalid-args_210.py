def test_create_alias_invalid_alias_name_too_long(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    long_name = "x" * 300
    alias_name = long_name

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", key_id,
    )

    assert result.returncode != 0
    assert "Exception" in result.stderr or "InvalidAliasName" in result.stderr

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert not any(a.get("AliasName") == "alias/" + long_name for a in aliases)
    assert not any(a.get("AliasName") == long_name for a in aliases)