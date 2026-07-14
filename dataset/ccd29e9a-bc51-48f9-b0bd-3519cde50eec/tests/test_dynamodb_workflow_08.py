from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_idempotent_then_get(ddb_client, cli, tmp_path):
    ddb_client.create_table(
        TableName="WfIdem1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "WfIdem1",
        "--key", '{"pk":{"S":"absent"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfIdem1", Key={"pk": {"S": "absent"}})
    assert "Item" not in resp
