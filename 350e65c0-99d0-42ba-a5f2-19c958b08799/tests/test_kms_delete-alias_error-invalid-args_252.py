def test_delete_alias_invalid_args(cli, kms):
    # Seed a real key and alias so state exists and remains untouched by the bad call
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = "alias/test-invalid-args-alias"
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    # Run the command with an unknown/invalid flag — must be rejected as an arg error
    result = cli(
        "kms", "delete-alias",
        "--alias-name", alias_name,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    # argparse-style rejection of an unknown argument
    assert "attribute-definitions" in result.stderr or "argument" in result.stderr.lower()

    # The alias must still exist, unchanged, because the command never ran
    aliases = kms.rpc("ListAliases", {})["Aliases"]
    match = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(match) == 1
    assert match[0].get("TargetKeyId") == key_id