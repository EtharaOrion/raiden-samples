def test_create_user_pool_client_nonexistent_user_pool(cli, cognito):
    pool_name = "client-error-nonexistent-pool"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    existing_pool_id = created["UserPool"]["Id"]

    baseline = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": existing_pool_id, "MaxResults": 60},
    )
    assert baseline["UserPoolClients"] == []

    replacement = "a" if existing_pool_id[-1] != "a" else "b"
    nonexistent_pool_id = existing_pool_id[:-1] + replacement

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        nonexistent_pool_id,
        "--client-name",
        "must-not-be-created",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    described = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": existing_pool_id},
    )
    assert described["UserPool"]["Name"] == pool_name

    clients_after = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": existing_pool_id, "MaxResults": 60},
    )
    assert clients_after["UserPoolClients"] == []