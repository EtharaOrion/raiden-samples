def test_encrypt_pending_deletion_invalid_state(cli, kms, tmp_path):
    import base64, json

    # Create a key to encrypt with
    created = kms.rpc("CreateKey", {"Description": "encrypt invalid state test"})
    key_id = created["KeyMetadata"]["KeyId"]

    # Schedule deletion -> KeyState becomes PendingDeletion
    kms.rpc("ScheduleKeyDeletion", {"KeyId": key_id, "PendingWindowInDays": 7})

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"

    plaintext = base64.b64encode(b"secret data").decode()

    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)

    assert result.returncode != 0
    assert "KMSInvalidStateException" in result.stderr

    # Key still exists and remains PendingDeletion
    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyState"] == "PendingDeletion"