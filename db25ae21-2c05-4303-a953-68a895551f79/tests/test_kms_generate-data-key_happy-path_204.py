import base64
import json


def test_generate_data_key_happy_path(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "gdk-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_256",
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "Plaintext" in out
    assert "CiphertextBlob" in out
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # The encrypted data key must decrypt back to the plaintext copy via KMS.
    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext