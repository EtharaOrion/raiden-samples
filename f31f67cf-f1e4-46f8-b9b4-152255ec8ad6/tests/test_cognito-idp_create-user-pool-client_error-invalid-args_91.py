def test_create_user_pool_client_missing_user_pool_id(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "missing-user-pool-id-test"},
    )["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    assert before["UserPoolClients"] == []

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--client-name",
        "invalid-args-client",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--user-pool-id" in result.stderr

    after = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    assert after["UserPoolClients"] == []