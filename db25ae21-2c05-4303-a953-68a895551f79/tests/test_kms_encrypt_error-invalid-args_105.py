def test_encrypt_invalid_args_unknown_flag(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", "aGVsbG8=",
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "attribute-definitions" in result.stderr or "Unknown" in result.stderr or "unknown" in result.stderr

    # Key remains present and usable
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["Enabled"] is True