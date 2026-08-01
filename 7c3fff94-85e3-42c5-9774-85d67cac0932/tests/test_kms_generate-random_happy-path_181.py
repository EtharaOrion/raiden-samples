def test_generate_random_happy_path(cli, kms):
    import base64
    import json

    number_of_bytes = 32

    result = cli(
        "kms",
        "generate-random",
        "--number-of-bytes",
        str(number_of_bytes),
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert set(output) >= {"Plaintext"}
    assert len(base64.b64decode(output["Plaintext"], validate=True)) == number_of_bytes

    observed = kms.rpc("GenerateRandom", {"NumberOfBytes": number_of_bytes})
    assert set(observed) >= {"Plaintext"}
    assert len(base64.b64decode(observed["Plaintext"], validate=True)) == number_of_bytes