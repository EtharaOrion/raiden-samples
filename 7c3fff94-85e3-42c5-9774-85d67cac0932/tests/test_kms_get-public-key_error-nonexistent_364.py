def test_get_public_key_nonexistent(cli, kms, tmp_path):
    created = kms.rpc(
        "CreateKey",
        {"KeyUsage": "SIGN_VERIFY", "KeySpec": "RSA_2048"},
    )
    key_id = created["KeyMetadata"]["KeyId"]
    missing_alias = f"alias/nonexistent-{key_id}"

    result = cli("kms", "get-public-key", "--key-id", missing_alias)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyUsage"] == "SIGN_VERIFY"
    assert metadata["KeySpec"] == "RSA_2048"

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert all(alias["AliasName"] != missing_alias for alias in aliases)