def test_update_user_pool_client_enables_prevent_user_existence_errors(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-client-prevent-existence-errors-pool"},
    )["UserPool"]
    user_pool_id = pool["Id"]

    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": user_pool_id,
            "ClientName": "update-client-prevent-existence-errors-client",
        },
    )["UserPoolClient"]
    client_id = client["ClientId"]

    before = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": user_pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert before.get("PreventUserExistenceErrors") != "ENABLED"

    result = cli(
        "cognito-idp",
        "update-user-pool-client",
        "--user-pool-id",
        user_pool_id,
        "--client-id",
        client_id,
        "--prevent-user-existence-errors",
        "ENABLED",
    )
    assert result.returncode == 0

    updated = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": user_pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert updated["UserPoolId"] == user_pool_id
    assert updated["ClientId"] == client_id
    assert updated["PreventUserExistenceErrors"] == "ENABLED"