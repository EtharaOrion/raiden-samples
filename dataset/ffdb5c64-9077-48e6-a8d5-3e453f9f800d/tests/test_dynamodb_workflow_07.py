from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_fails_no_mutation(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfTblUpdCond",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfTblUpdCond",
                 "--item", '{"pk":{"S":"e1"},"v":{"S":"keep"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "WfTblUpdCond",
                 "--key", '{"pk":{"S":"e1"}}',
                 "--update-expression", "SET v = :n",
                 "--expression-attribute-values", '{":n":{"S":"changed"},":old":{"S":"nomatch"}}',
                 "--condition-expression", "v = :old")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTblUpdCond", Key={"pk": {"S": "e1"}})
    assert from_item(resp["Item"])["v"] == "keep"
