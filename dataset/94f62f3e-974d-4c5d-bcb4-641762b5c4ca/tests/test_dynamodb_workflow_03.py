from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_idempotent_missing_key(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf_DelIdem1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "Wf_DelIdem1",
        "--key", '{"pk":{"S":"nope"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf_DelIdem1", Key={"pk": {"S": "nope"}})
    assert "Item" not in resp
