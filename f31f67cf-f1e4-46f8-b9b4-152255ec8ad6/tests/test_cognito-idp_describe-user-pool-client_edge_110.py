def test_describe_user_pool_client_existing_client(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "describe-client-edge-pool"},
    )["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "describe-client-edge-app",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--user-pool-id",
        pool["Id"],
        "--client-id",
        client["ClientId"],
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["UserPoolClient"]["UserPoolId"] == pool["Id"]
    assert output["UserPoolClient"]["ClientId"] == client["ClientId"]
    assert output["UserPoolClient"]["ClientName"] == "describe-client-edge-app"

    stored = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert stored["UserPoolId"] == pool["Id"]
    assert stored["ClientId"] == client["ClientId"]
    assert stored["ClientName"] == "describe-client-edge-app"