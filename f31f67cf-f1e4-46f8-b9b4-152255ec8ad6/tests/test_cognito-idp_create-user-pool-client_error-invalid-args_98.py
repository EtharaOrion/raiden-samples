def test_create_user_pool_client_rejects_unknown_flag_without_creating_client(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "invalid-flag-test-pool"})["UserPool"]
    pool_id = pool["Id"]

    clients_before = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )["UserPoolClients"]
    assert clients_before == []

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-name",
        "should-not-be-created",
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "unknown option" in result.stderr.lower()

    clients_after = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )["UserPoolClients"]
    assert clients_after == []