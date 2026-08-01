def test_decrypt_invalid_args(cli, kms):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    ct = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": "aGVsbG8="})["CiphertextBlob"]

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ct,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    # Key remains intact and usable (state unchanged by the failed invalid command)
    md = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert md["KeyId"] == key_id
    assert md["Enabled"] is True

    # Round-trip sanity: the ciphertext still decrypts to the original plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ct})
    assert dec["Plaintext"] == "aGVsbG8="