from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_fail_unchanged(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfCondUpdTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )

    result = cli("dynamodb", "put-item", "--table-name", "WfCondUpdTbl",
                 "--item", '{"pk":{"S":"u1"},"v":{"S":"keep"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "update-item", "--table-name", "WfCondUpdTbl",
                 "--key", '{"pk":{"S":"u1"}}',
                 "--update-expression", "SET v = :new",
                 "--expression-attribute-values", '{":new":{"S":"mutated"},":chk":{"S":"nomatch"}}',
                 "--condition-expression", "v = :chk")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    resp = ddb_client.get_item(TableName="WfCondUpdTbl", Key={"pk": {"S": "u1"}})
    assert from_item(resp["Item"])["v"] == "keep"
