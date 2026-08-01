from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_null_type(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf74Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf74Table",
                 "--item", '{"pk":{"S":"nl1"},"empty":{"NULL":true}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf74Table", Key={"pk": {"S": "nl1"}})
    assert from_item(resp["Item"])["empty"] is None
