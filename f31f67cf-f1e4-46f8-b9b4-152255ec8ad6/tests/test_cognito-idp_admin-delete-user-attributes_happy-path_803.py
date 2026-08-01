def test_admin_delete_user_attributes_happy_path(cli, cognito):
    import uuid

    pool_name = f"adua-{uuid.uuid4().hex}"
    pool_id = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]["Id"]

    username = f"user-{uuid.uuid4().hex[:12]}@example.com"
    cognito.rpc(
        "AdminCreateUser",
        {
            "UserPoolId": pool_id,
            "Username": username,
            "MessageAction": "SUPPRESS",
        },
    )
    cognito.rpc(
        "AdminUpdateUserAttributes",
        {
            "UserPoolId": pool_id,
            "Username": username,
            "UserAttributes": [
                {"Name": "phone_number", "Value": "+15555550100"},
            ],
        },
    )

    before = cognito.rpc(
        "AdminGetUser",
        {"UserPoolId": pool_id, "Username": username},
    )
    before_names = {a["Name"] for a in before.get("UserAttributes", [])}
    assert "phone_number" in before_names

    result = cli(
        "cognito-idp",
        "admin-delete-user-attributes",
        "--user-pool-id",
        pool_id,
        "--username",
        username,
        "--user-attribute-names",
        "phone_number",
    )
    assert result.returncode == 0, result.stderr

    after = cognito.rpc(
        "AdminGetUser",
        {"UserPoolId": pool_id, "Username": username},
    )
    after_names = {a["Name"] for a in after.get("UserAttributes", [])}
    assert "phone_number" not in after_names
