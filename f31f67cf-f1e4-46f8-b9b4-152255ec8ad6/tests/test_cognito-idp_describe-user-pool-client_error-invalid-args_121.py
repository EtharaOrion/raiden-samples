def test_describe_user_pool_client_rejects_unknown_attribute_definitions(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "describe-client-invalid-args-pool"})["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "describe-client-invalid-args-client",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--user-pool-id",
        pool["Id"],
        "--client-id",
        client["ClientId"],
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    persisted = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert persisted["UserPoolId"] == pool["Id"]
    assert persisted["ClientId"] == client["ClientId"]
    assert persisted["ClientName"] == "describe-client-invalid-args-client"