def test_update_user_pool_client_with_only_required_arguments(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-client-required-only-pool"},
    )["UserPool"]
    user_pool_id = pool["Id"]

    created_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": user_pool_id,
            "ClientName": "required-only-client",
        },
    )["UserPoolClient"]
    client_id = created_client["ClientId"]

    result = cli(
        "cognito-idp",
        "update-user-pool-client",
        "--user-pool-id",
        user_pool_id,
        "--client-id",
        client_id,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["UserPoolClient"]["UserPoolId"] == user_pool_id
    assert output["UserPoolClient"]["ClientId"] == client_id

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": user_pool_id,
            "ClientId": client_id,
        },
    )["UserPoolClient"]
    assert described["UserPoolId"] == user_pool_id
    assert described["ClientId"] == client_id
    assert described["ClientName"] == "required-only-client"