def test_create_alias_invalid_args(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    alias_name = "alias/InvalidArgsAlias"
    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", key_id,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown" in result.stderr or "attribute-definitions" in result.stderr

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert not any(a.get("AliasName") == alias_name for a in aliases)