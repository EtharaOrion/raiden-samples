def test_encrypt_invalid_key_id_not_found(cli, kms, tmp_path):
    # Prerequisite: establish a real, valid key so the server is functional,
    # ensuring failure is due to the bogus key id, not an empty backend.
    created = kms.rpc("CreateKey", {"Description": "encrypt-error-baseline"})
    valid_key_id = created["KeyMetadata"]["KeyId"]
    assert valid_key_id

    # A syntactically-invalid / non-existent key id (400 'x' characters).
    bogus_key_id = "x" * 400

    plaintext_file = tmp_path / "plain.txt"
    plaintext_file.write_bytes(b"secret data")

    result = cli(
        "kms", "encrypt",
        "--key-id", bogus_key_id,
        "--plaintext", "fileb://" + str(plaintext_file),
    )

    # Must fail (non-zero) with a recognizable error category in stderr.
    assert result.returncode != 0
    combined = (result.stderr or "") + (result.stdout or "")
    assert (
        "NotFoundException" in combined
        or "NotFound" in combined
        or "ValidationException" in combined
        or "InvalidKeyUsage" in combined
    )

    # State assertion: the valid baseline key remains usable/unaffected,
    # confirming the server is healthy and only the bad request was rejected.
    desc = kms.rpc("DescribeKey", {"KeyId": valid_key_id})
    assert desc["KeyMetadata"]["KeyId"] == valid_key_id
    assert desc["KeyMetadata"]["Enabled"] is True