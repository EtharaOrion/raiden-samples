def test_describe_user_pool_happy_path(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "describe-pool-test"})
    pool_id = created["UserPool"]["Id"]

    result = cli("cognito-idp", "describe-user-pool", "--user-pool-id", pool_id)
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    assert payload["UserPool"]["Id"] == pool_id
    assert payload["UserPool"]["Name"] == "describe-pool-test"

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "describe-pool-test"