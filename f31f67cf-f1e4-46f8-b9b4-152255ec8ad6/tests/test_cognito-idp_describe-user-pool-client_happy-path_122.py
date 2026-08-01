def test_describe_user_pool_client_happy_path(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "describe-client-test-pool"},
    )["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "describe-client-test-app",
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
    assert output["UserPoolClient"]["ClientId"] == client["ClientId"]
    assert output["UserPoolClient"]["ClientName"] == "describe-client-test-app"
    assert output["UserPoolClient"]["UserPoolId"] == pool["Id"]

    stored_client = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert stored_client["ClientId"] == client["ClientId"]
    assert stored_client["ClientName"] == "describe-client-test-app"
    assert stored_client["UserPoolId"] == pool["Id"]