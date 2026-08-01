def test_create_alias_invalid_alias_name(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "alias-error-test"})
    key_id = key["KeyMetadata"]["KeyId"]

    # Alias name that does not begin with the required 'alias/' prefix
    bad_alias = "not-a-valid-alias-name"

    result = cli(
        "kms", "create-alias",
        "--alias-name", bad_alias,
        "--target-key-id", key_id,
    )

    assert result.returncode != 0
    assert "InvalidAliasName" in result.stderr or "Exception" in result.stderr

    # Assert no such alias was created
    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    names = [a.get("AliasName") for a in aliases]
    assert bad_alias not in names
    assert "alias/" + bad_alias not in names