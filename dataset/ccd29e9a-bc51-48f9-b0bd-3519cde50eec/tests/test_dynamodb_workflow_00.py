from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_get(ddb_client, cli, tmp_path):
    ddb_client.create_table(
        TableName="WfUpd1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfUpd1", Item={"pk": {"S": "a"}, "status": {"S": "old"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "WfUpd1",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"new"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfUpd1", Key={"pk": {"S": "a"}})
    assert resp["Item"]["status"]["S"] == "new"
