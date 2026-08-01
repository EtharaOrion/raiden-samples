def test_delete_user_pool_client_missing_user_pool_id(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-client-missing-pool-id"},
    )["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "client-must-remain",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "delete-user-pool-client",
        "--client-id",
        client["ClientId"],
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    remaining = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert remaining["ClientId"] == client["ClientId"]
    assert remaining["ClientName"] == "client-must-remain"
    assert remaining["UserPoolId"] == pool["Id"]