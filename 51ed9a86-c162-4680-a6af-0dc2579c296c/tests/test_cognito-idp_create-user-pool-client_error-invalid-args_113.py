def test_create_user_pool_client_invalid_args(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "invalid-args-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", pool_id,
        "--client-name", "badclient",
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "Unknown" in result.stderr or "Invalid" in result.stderr

    # No client should have been created in the pool.
    listed = cognito.rpc("ListUserPoolClients", {"UserPoolId": pool_id, "MaxResults": 60})
    names = [c.get("ClientName") for c in listed.get("UserPoolClients", [])]
    assert "badclient" not in names