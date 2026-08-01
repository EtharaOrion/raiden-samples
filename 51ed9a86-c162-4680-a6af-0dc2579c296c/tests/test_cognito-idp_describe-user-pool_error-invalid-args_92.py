def test_describe_user_pool_nonexistent_id_error(cli, cognito):
    # Seed a real pool so the service is functional, then confirm it exists.
    created = cognito.rpc("CreateUserPool", {"PoolName": "seed-pool"})
    pool_id = created["UserPool"]["Id"]
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id

    # Now describe a non-existent pool id -> must fail with a service error.
    missing_id = "local_doesnotexist999"
    result = cli("cognito-idp", "describe-user-pool", "--user-pool-id", missing_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "NotFound" in result.stderr

    # The seeded pool must still be intact and describable.
    still = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert still["UserPool"]["Id"] == pool_id