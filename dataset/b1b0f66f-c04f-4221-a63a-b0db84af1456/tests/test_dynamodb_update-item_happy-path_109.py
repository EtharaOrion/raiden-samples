from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_sets_new_attribute(cli, ddb_client):
    ddb_client.create_table(
        TableName="UpdTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="UpdTbl",
        Item={"pk": {"S": "item1"}, "status": {"S": "old"}},
    )

    result = cli(
        "dynamodb", "update-item",
        "--table-name", "UpdTbl",
        "--key", '{"pk":{"S":"item1"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )
    assert result.returncode == 0

    resp = ddb_client.get_item(
        TableName="UpdTbl",
        Key={"pk": {"S": "item1"}},
    )
    assert resp.get("Item") is not None
    assert resp["Item"]["status"] == {"S": "active"}