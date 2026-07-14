from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_condition_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDelCond",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfDelCond", Item={"pk": {"S": "keep"}, "v": {"N": "10"}})
    result = cli("dynamodb", "delete-item", "--table-name", "WfDelCond",
                 "--key", '{"pk":{"S":"keep"}}',
                 "--condition-expression", "v = :expected",
                 "--expression-attribute-values", '{":expected":{"N":"77"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfDelCond", Key={"pk": {"S": "keep"}}, ConsistentRead=True)
    assert "Item" in resp
    assert from_item(resp["Item"])["v"] == 10
