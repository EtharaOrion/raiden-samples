from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_conditional_fail(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDel3",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfDel3", Item={"pk": {"S": "a"}, "v": {"S": "keep"}})
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "WfDel3",
        "--key", '{"pk":{"S":"a"}}',
        "--condition-expression", "v = :expected",
        "--expression-attribute-values", '{":expected":{"S":"wrong"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfDel3", Key={"pk": {"S": "a"}})
    assert from_item(resp["Item"])["v"] == "keep"
