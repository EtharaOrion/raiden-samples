def test_delete_user_pool_nonexistent_pool_errors(cli, cognito):
    # Seed a real pool so we know the service is functional, then target a
    # non-existent pool id to force an error category from DeleteUserPool.
    created = cognito.rpc("CreateUserPool", {"PoolName": "seed-pool-for-delete-test"})
    real_pool_id = created["UserPool"]["Id"]

    missing_pool_id = "local_doesnotexist999"

    result = cli(
        "cognito-idp", "delete-user-pool",
        "--user-pool-id", missing_pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "NotFound" in result.stderr

    # The real, seeded pool must remain intact and describable.
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": real_pool_id})
    assert described["UserPool"]["Id"] == real_pool_id

    # Cleanup the seed pool.
    cognito.rpc("DeleteUserPool", {"UserPoolId": real_pool_id})