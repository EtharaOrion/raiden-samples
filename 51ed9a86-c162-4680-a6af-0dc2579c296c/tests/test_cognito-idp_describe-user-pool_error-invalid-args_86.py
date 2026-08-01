def test_describe_user_pool_duplicate_arg_invalid(cli, cognito, tmp_path):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "dup-arg-pool"})
    pool_id = pool["UserPool"]["Id"]

    # Sanity: the pool exists and is describable
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id

    # Pass --user-pool-id twice: second value is a malformed/nonexistent id
    bogus_id = "not_a_valid_pool_id"
    result = cli(
        "cognito-idp", "describe-user-pool",
        "--user-pool-id", pool_id,
        "--user-pool-id", bogus_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "ResourceNotFoundException" in result.stderr
        or "InvalidParameterException" in result.stderr
    )

    # State assertion: original pool is untouched and still describable
    still = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert still["UserPool"]["Id"] == pool_id