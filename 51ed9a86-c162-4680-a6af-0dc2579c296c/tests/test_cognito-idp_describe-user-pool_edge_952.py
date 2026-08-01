def test_describe_user_pool_exposes_configuration_blocks(cli, cognito):
    import json
    import uuid

    name = "pool-config-" + uuid.uuid4().hex[:8]
    pool_id = cognito.rpc("CreateUserPool", {"PoolName": name})["UserPool"]["Id"]

    result = cli("cognito-idp", "describe-user-pool", "--user-pool-id", pool_id)
    assert result.returncode == 0, result.stderr

    pool = json.loads(result.stdout)["UserPool"]
    for field in ("AdminCreateUserConfig", "EmailConfiguration", "LambdaConfig",
                  "Policies", "SchemaAttributes", "Arn", "EstimatedNumberOfUsers"):
        assert field in pool, field

    assert pool["EmailConfiguration"]["EmailSendingAccount"] == "COGNITO_DEFAULT"
    assert pool["AdminCreateUserConfig"]["AllowAdminCreateUserOnly"] is False
    assert isinstance(pool["SchemaAttributes"], list)
