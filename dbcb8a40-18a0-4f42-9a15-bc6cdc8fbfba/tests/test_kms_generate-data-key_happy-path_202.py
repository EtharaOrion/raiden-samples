import json
import base64


def test_generate_data_key_happy_path(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "gdk test"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--number-of-bytes", "32",
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    ciphertext = out["CiphertextBlob"]
    assert ciphertext

    # Independent read: the encrypted data key must decrypt back to the plaintext.
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext

    # The KMS key used must still exist and be enabled.
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Enabled"] is True