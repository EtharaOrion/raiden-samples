def test_generate_random_maximum_length(cli, kms):
    import base64
    import json

    created = kms.rpc("CreateKey", {"Description": "generate-random state sentinel"})
    key_id = created["KeyMetadata"]["KeyId"]
    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]

    result = cli("kms", "generate-random", "--number-of-bytes", "1024")

    assert result.returncode == 0
    output = json.loads(result.stdout)
    random_bytes = base64.b64decode(output["Plaintext"], validate=True)
    assert len(random_bytes) == 1024

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == before["KeyId"]
    assert after["KeyState"] == before["KeyState"]
    assert after["Enabled"] == before["Enabled"]