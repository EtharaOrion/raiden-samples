def test_describe_user_pool_client_nonexistent(cli, cognito, tmp_path):
    pool_name = f"describe-client-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]
    nonexistent_client_id = "nonexistentclient123"

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-id",
        nonexistent_client_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    described_pool = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described_pool["UserPool"]["Id"] == pool_id
    assert described_pool["UserPool"]["Name"] == pool_name

    clients = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    assert all(
        client["ClientId"] != nonexistent_client_id
        for client in clients.get("UserPoolClients", [])
    )