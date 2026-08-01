def test_kms_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    import base64

    # Provide a bogus ciphertext blob that was never produced by KMS.
    bogus = base64.b64encode(b"this-is-not-a-valid-kms-ciphertext-blob").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidCiphertextException" in result.stderr

    # Sanity check the backend is alive and did not create spurious state.
    listing = kms.rpc("ListKeys", {})
    assert "Keys" in listing