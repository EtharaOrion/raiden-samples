from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_conditional_not_exists_fails(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfTblCond",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfTblCond",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"first"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTblCond",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"second"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTblCond", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"])["v"] == "first"
