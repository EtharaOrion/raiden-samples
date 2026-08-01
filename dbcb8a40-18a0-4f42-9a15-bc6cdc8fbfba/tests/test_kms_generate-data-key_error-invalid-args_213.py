def test_generate_data_key_invalid_number_of_bytes(cli, kms):
    created = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT", "KeySpec": "SYMMETRIC_DEFAULT"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "generate-data-key", "--key-id", key_id, "--number-of-bytes", "0")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ValidationException" in result.stderr or "Validation" in result.stderr or "Invalid" in result.stderr

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Enabled"] is True