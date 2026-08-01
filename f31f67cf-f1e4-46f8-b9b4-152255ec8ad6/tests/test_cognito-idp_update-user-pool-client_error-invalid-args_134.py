def test_update_user_pool_client_rejects_unknown_flag(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-client-invalid-args-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "update-client-invalid-args-client",
        },
    )["UserPoolClient"]
    client_id = client["ClientId"]

    before = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert before["ClientName"] == "update-client-invalid-args-client"

    result = cli(
        "cognito-idp",
        "update-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-id",
        client_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert after["UserPoolId"] == pool_id
    assert after["ClientId"] == client_id
    assert after["ClientName"] == before["ClientName"]