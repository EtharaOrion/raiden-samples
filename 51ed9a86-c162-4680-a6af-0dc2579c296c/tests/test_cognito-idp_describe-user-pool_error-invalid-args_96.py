def test_describe_user_pool_nonexistent_id_errors(cli, cognito):
    # Ensure a valid pool exists so the server is functional, then query a bogus id.
    created = cognito.rpc("CreateUserPool", {"PoolName": "seed-pool"})
    valid_id = created["UserPool"]["Id"]
    assert valid_id

    # Sanity: the valid pool is describable via the raw client.
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": valid_id})
    assert described["UserPool"]["Id"] == valid_id

    # Query a user pool id that does not exist -> service error surfaced.
    bogus_id = "local_nonexistentpoolid"
    result = cli("cognito-idp", "describe-user-pool", "--user-pool-id", bogus_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr

    # The valid pool state remains intact and readable.
    still = cognito.rpc("DescribeUserPool", {"UserPoolId": valid_id})
    assert still["UserPool"]["Id"] == valid_id