def test_generate_random_happy_path(cli, kms, tmp_path):
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
    assert len(base64.b64decode(output["Plaintext"], validate=True)) == number_of_bytes

    service_result = kms.rpc(
        "GenerateRandom",
        {"NumberOfBytes": number_of_bytes},
    )
    assert len(
        base64.b64decode(service_result["Plaintext"], validate=True)
    ) == number_of_bytes