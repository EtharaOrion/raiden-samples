def test_create_alias_rejects_unknown_attribute_definitions(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "create-alias invalid arguments test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = f"alias/invalid-args-{key_id}"

    before = kms.rpc("ListAliases", {})
    before_aliases = {
        (alias["AliasName"], alias.get("TargetKeyId"))
        for alias in before["Aliases"]
    }
    assert alias_name not in {name for name, _ in before_aliases}

    result = cli(
        "kms",
        "create-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        key_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("ListAliases", {})
    after_aliases = {
        (alias["AliasName"], alias.get("TargetKeyId"))
        for alias in after["Aliases"]
    }
    assert after_aliases == before_aliases
    assert alias_name not in {name for name, _ in after_aliases}