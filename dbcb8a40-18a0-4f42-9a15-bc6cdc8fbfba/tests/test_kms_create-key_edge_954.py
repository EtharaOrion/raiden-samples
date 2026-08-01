def test_create_key_response_carries_service_defaults(cli, kms):
    import json
    import re

    result = cli("kms", "create-key", "--description", "create-defaults")
    assert result.returncode == 0, result.stderr

    md = json.loads(result.stdout)["KeyMetadata"]

    assert md["Enabled"] is True
    assert md["KeyState"] == "Enabled"
    assert md["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert md["Origin"] == "AWS_KMS"
    assert md["KeyManager"] == "CUSTOMER"
    assert md["KeySpec"] == "SYMMETRIC_DEFAULT"
    assert md["EncryptionAlgorithms"] == ["SYMMETRIC_DEFAULT"]
    assert re.fullmatch(
        r"arn:aws:kms:[a-z0-9-]+:\d{12}:key/" + re.escape(md["KeyId"]), md["Arn"]
    )

    described = kms.rpc("DescribeKey", {"KeyId": md["KeyId"]})["KeyMetadata"]
    assert described["KeyId"] == md["KeyId"]
    assert described["Description"] == "create-defaults"
