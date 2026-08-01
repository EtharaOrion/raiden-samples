def test_create_user_pool_returns_full_pool_document(cli, cognito):
    import json
    import re
    import uuid

    name = "pool-contract-" + uuid.uuid4().hex[:8]
    result = cli("cognito-idp", "create-user-pool", "--pool-name", name)
    assert result.returncode == 0, result.stderr

    pool = json.loads(result.stdout)["UserPool"]

    assert pool["Name"] == name
    assert pool["MfaConfiguration"] == "OFF"
    assert pool["EstimatedNumberOfUsers"] == 0
    assert re.fullmatch(
        r"arn:aws:cognito-idp:[^:]+:[^:]+:userpool/" + re.escape(pool["Id"]), pool["Arn"]
    )

    policy = pool["Policies"]["PasswordPolicy"]
    assert policy["MinimumLength"] == 8
    assert policy["RequireUppercase"] is True
    assert policy["RequireLowercase"] is True
    assert policy["RequireNumbers"] is True
    assert policy["RequireSymbols"] is True

    schema_names = {a["Name"] for a in pool["SchemaAttributes"]}
    assert "sub" in schema_names
