from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_binary_bool(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf22Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf22Table",
                 "--item", '{"pk":{"S":"b1"},"flag":{"BOOL":true}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf22Table",
                 "--key", '{"pk":{"S":"b1"}}',
                 "--update-expression", "SET flag = :f",
                 "--expression-attribute-values", '{":f":{"BOOL":false}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf22Table", Key={"pk": {"S": "b1"}})
    assert from_item(resp["Item"])["flag"] is False
