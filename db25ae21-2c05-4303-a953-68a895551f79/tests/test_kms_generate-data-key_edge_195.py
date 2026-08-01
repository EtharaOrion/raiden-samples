import json
import base64


def test_generate_data_key_with_grant_tokens(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "gdk-grant-token-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_256",
        "--grant-tokens", "xxxxxxxxxx",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32  # AES_256 => 32 bytes

    # Verify the ciphertext blob decrypts back to the plaintext data key.
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id