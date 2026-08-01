def test_describe_user_pool_missing_required_arg(cli, cognito, tmp_path):
    # Seed a valid pool so the failure is clearly due to the missing arg, not empty state.
    created = cognito.rpc("CreateUserPool", {"PoolName": "seed-pool"})
    pool_id = created["UserPool"]["Id"]

    # Run describe-user-pool WITHOUT the required --user-pool-id.
    result = cli("cognito-idp", "describe-user-pool")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr.lower()
    assert "user-pool-id" in stderr or "usagerror" in stderr or "required" in stderr

    # The seeded pool must still be describable via the API (state unaffected).
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "seed-pool"