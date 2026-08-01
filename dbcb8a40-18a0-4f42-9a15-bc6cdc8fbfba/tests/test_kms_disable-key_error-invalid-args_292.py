def test_disable_key_missing_key_id_errors(cli, kms):
    # Seed a valid key so the only problem is the missing required arg
    created = kms.rpc("CreateKey", {"Description": "seed for disable-key error"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert created["KeyMetadata"]["Enabled"] is True

    # Run disable-key WITHOUT the required --key-id
    result = cli("kms", "disable-key")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "key-id" in result.stderr.lower()

    # The seeded key must remain enabled (command had no effect)
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is True
    assert described["KeyMetadata"]["KeyState"] == "Enabled"