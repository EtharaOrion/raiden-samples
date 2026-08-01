from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_update_returns_zero(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf76Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf76Table",
                 "--item", '{"pk":{"S":"rz1"},"c":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf76Table",
                 "--key", '{"pk":{"S":"rz1"}}',
                 "--update-expression", "SET c = c + :inc",
                 "--expression-attribute-values", '{":inc":{"N":"10"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf76Table", Key={"pk": {"S": "rz1"}})
    assert from_item(resp["Item"])["c"] == 11
