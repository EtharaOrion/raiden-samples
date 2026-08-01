def test_update_user_pool_client_with_only_required_arguments(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-client-required-only-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    created_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "update-client-required-only",
        },
    )["UserPoolClient"]
    client_id = created_client["ClientId"]

    result = cli(
        "cognito-idp",
        "update-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-id",
        client_id,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["UserPoolClient"]["UserPoolId"] == pool_id
    assert output["UserPoolClient"]["ClientId"] == client_id

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert described["UserPoolId"] == pool_id
    assert described["ClientId"] == client_id
    assert described["ClientName"] == "update-client-required-only"