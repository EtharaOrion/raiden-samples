import base64
import json


def test_generate_data_key_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "gdk-happy"})
    key_id = key["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--number-of-bytes", "32",
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out

    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # The returned KeyId should resolve to our key
    desc = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert desc["KeyMetadata"]["KeyId"] == key_id

    # The encrypted data key round-trips back to the plaintext.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext