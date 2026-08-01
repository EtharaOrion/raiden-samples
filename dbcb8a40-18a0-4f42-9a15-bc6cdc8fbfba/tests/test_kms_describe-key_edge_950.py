def test_describe_key_returns_full_key_metadata(cli, kms):
    import json
    import re

    created = kms.rpc("CreateKey", {"Description": "metadata-contract"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "describe-key", "--key-id", key_id)
    assert result.returncode == 0, result.stderr

    md = json.loads(result.stdout)["KeyMetadata"]

    assert md["KeyId"] == key_id
    assert md["Enabled"] is True
    assert md["KeyState"] == "Enabled"
    assert md["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert md["Origin"] == "AWS_KMS"
    assert md["KeyManager"] == "CUSTOMER"
    assert md["KeySpec"] == "SYMMETRIC_DEFAULT"
    assert md["CustomerMasterKeySpec"] == "SYMMETRIC_DEFAULT"
    assert md["EncryptionAlgorithms"] == ["SYMMETRIC_DEFAULT"]
    assert md["Description"] == "metadata-contract"
    assert re.fullmatch(r"\d{12}", str(md["AWSAccountId"]))
    assert re.fullmatch(
        r"arn:aws:kms:[a-z0-9-]+:\d{12}:key/" + re.escape(key_id), md["Arn"]
    )
