def test_update_user_pool_client_with_required_ids(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-client-required-ids-pool"},
    )["UserPool"]
    user_pool_id = pool["Id"]

    created_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": user_pool_id,
            "ClientName": "client-before-update",
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

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["UserPoolClient"]["UserPoolId"] == user_pool_id
    assert output["UserPoolClient"]["ClientId"] == client_id
    assert output["UserPoolClient"]["ClientName"] == "client-before-update"

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": user_pool_id,
            "ClientId": client_id,
        },
    )["UserPoolClient"]
    assert described["UserPoolId"] == user_pool_id
    assert described["ClientId"] == client_id
    assert described["ClientName"] == "client-before-update"