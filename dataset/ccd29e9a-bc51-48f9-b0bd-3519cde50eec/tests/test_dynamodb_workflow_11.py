from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_deleteitem_then_get(ddb_client, cli, tmp_path):
    ddb_client.create_table(
        TableName="WfChain1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfChain1", Item={"pk": {"S": "k"}, "n": {"N": "1"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "WfChain1",
        "--key", '{"pk":{"S":"k"}}',
        "--update-expression", "SET n = :v",
        "--expression-attribute-values", '{":v":{"N":"99"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfChain1", Key={"pk": {"S": "k"}})
    assert resp["Item"]["n"]["N"] == "99"
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "WfChain1",
        "--key", '{"pk":{"S":"k"}}',
    )
    assert result.returncode == 0
    resp2 = ddb_client.get_item(TableName="WfChain1", Key={"pk": {"S": "k"}})
    assert "Item" not in resp2
