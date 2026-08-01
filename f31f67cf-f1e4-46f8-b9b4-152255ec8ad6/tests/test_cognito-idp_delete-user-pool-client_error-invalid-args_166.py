def test_delete_user_pool_client_missing_client_id(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-client-missing-argument-pool"},
    )["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "client-that-must-remain",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "delete-user-pool-client",
        "--user-pool-id",
        pool["Id"],
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--client-id" in result.stderr

    remaining = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert remaining["ClientId"] == client["ClientId"]
    assert remaining["ClientName"] == "client-that-must-remain"
    assert remaining["UserPoolId"] == pool["Id"]