from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_overwrites_removes_old_attrs(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf45Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf45Table",
                 "--item", '{"pk":{"S":"ov1"},"a":{"S":"x"},"b":{"S":"y"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf45Table",
                 "--item", '{"pk":{"S":"ov1"},"a":{"S":"z"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf45Table", Key={"pk": {"S": "ov1"}})
    item = from_item(resp["Item"])
    assert item["a"] == "z" and "b" not in item
