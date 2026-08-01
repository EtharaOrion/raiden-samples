from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_exists_success(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf32Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf32Table",
                 "--item", '{"pk":{"S":"ce1"},"v":{"S":"one"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf32Table",
                 "--item", '{"pk":{"S":"ce1"},"v":{"S":"two"}}',
                 "--condition-expression", "attribute_exists(pk)")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf32Table", Key={"pk": {"S": "ce1"}})
    assert from_item(resp["Item"])["v"] == "two"
