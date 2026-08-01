def test_describe_user_pool_client_happy_path(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "describe-client-test-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    created_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "describe-client-test-app",
        },
    )["UserPoolClient"]
    client_id = created_client["ClientId"]

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-id",
        client_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["UserPoolClient"]["UserPoolId"] == pool_id
    assert output["UserPoolClient"]["ClientId"] == client_id
    assert output["UserPoolClient"]["ClientName"] == "describe-client-test-app"

    stored_client = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientId": client_id,
        },
    )["UserPoolClient"]
    assert stored_client["UserPoolId"] == pool_id
    assert stored_client["ClientId"] == client_id
    assert stored_client["ClientName"] == "describe-client-test-app"