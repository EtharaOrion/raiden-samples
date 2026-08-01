import json
import base64

def test_generate_data_key_with_grant_tokens_roundtrip(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "gdk-test"})
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
    ciphertext = out["CiphertextBlob"]
    plaintext = out["Plaintext"]

    # AES_256 => 32 bytes of plaintext key material
    assert len(base64.b64decode(plaintext)) == 32

    # Verify the returned key id resolves to our created key
    described = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id

    # Independent read: decrypting the encrypted data key returns the same plaintext
    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext})
    assert decrypted["Plaintext"] == plaintext
    assert decrypted["KeyId"].endswith(key_id) or decrypted["KeyId"] == key_id