def test_encrypt_pending_deletion_invalid_state(cli, kms, tmp_path):
    create = kms.rpc("CreateKey", {"Description": "encrypt-invalid-state"})
    key_id = create["KeyMetadata"]["KeyId"]

    sched = kms.rpc("ScheduleKeyDeletion", {"KeyId": key_id, "PendingWindowInDays": 7})
    assert sched["KeyState"] == "PendingDeletion" if "KeyState" in sched else True

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"

    import base64
    plaintext = base64.b64encode(b"secret-data").decode()

    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "KMSInvalidStateException" in result.stderr

    still = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert still["KeyMetadata"]["KeyState"] == "PendingDeletion"