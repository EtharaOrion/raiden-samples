def test_create_alias_rejects_empty_alias_name(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "target for invalid alias test"})
    key_id = key["KeyMetadata"]["KeyId"]

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    alias_targets_before = {
        (alias["AliasName"], alias.get("TargetKeyId")) for alias in aliases_before
    }

    result = cli(
        "kms",
        "create-alias",
        "--alias-name",
        "",
        "--target-key-id",
        key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "Invalid length" in result.stderr
        or "InvalidAliasNameException" in result.stderr
    )

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    alias_targets_after = {
        (alias["AliasName"], alias.get("TargetKeyId")) for alias in aliases_after
    }
    assert alias_targets_after == alias_targets_before
    assert all(alias["AliasName"] != "" for alias in aliases_after)