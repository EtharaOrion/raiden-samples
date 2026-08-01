def test_delete_user_pool_client_rejects_unknown_flag(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "invalid-args-delete-client-pool"})[
        "UserPool"
    ]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "client-must-not-be-deleted",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "delete-user-pool-client",
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

    remaining = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert remaining["UserPoolId"] == pool["Id"]
    assert remaining["ClientId"] == client["ClientId"]
    assert remaining["ClientName"] == "client-must-not-be-deleted"