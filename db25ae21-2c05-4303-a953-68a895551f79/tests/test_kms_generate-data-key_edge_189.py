import base64
import json


def test_generate_data_key_number_of_bytes(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "gen-data-key-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--number-of-bytes", "1024",
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "Plaintext" in out
    assert "CiphertextBlob" in out
    assert "KeyId" in out

    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 1024

    # The returned KeyId must resolve to the same key we created.
    described = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id

    # The encrypted data key must decrypt back to the plaintext data key.
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id