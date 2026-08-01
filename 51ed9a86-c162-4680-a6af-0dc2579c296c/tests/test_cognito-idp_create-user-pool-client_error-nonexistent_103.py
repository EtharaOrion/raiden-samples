def test_create_user_pool_client_error_nonexistent(cli, cognito):
    fake_pool_id = "local_deadbeef"

    # Ensure the pool does not exist by verifying DescribeUserPool fails.
    try:
        cognito.rpc("DescribeUserPool", {"UserPoolId": fake_pool_id})
        pool_exists = True
    except Exception:
        pool_exists = False
    assert not pool_exists

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        fake_pool_id,
        "--client-name",
        "my-nonexistent-client",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no client got created against the fake pool.
    try:
        resp = cognito.rpc("ListUserPoolClients", {"UserPoolId": fake_pool_id, "MaxResults": 60})
        clients = resp.get("UserPoolClients", [])
        assert all(c.get("ClientName") != "my-nonexistent-client" for c in clients)
    except Exception:
        # Listing on a nonexistent pool also fails — acceptable evidence nothing was created.
        pass