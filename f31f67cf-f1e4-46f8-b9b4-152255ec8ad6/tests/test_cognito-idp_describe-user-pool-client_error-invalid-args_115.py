def test_describe_user_pool_client_rejects_unknown_flag(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "invalid-args-pool"})["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "invalid-args-client",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--user-pool-id",
        pool["Id"],
        "--client-id",
        client["ClientId"],
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    stored_client = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert stored_client["UserPoolId"] == pool["Id"]
    assert stored_client["ClientId"] == client["ClientId"]
    assert stored_client["ClientName"] == "invalid-args-client"