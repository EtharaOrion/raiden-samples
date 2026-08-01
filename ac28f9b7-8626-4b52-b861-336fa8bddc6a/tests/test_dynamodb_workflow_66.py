from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_fail_leaves_absent(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf67Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf67Table",
                 "--item", '{"pk":{"S":"fa1"}}',
                 "--condition-expression", "attribute_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf67Table", Key={"pk": {"S": "fa1"}})
    assert "Item" not in resp
