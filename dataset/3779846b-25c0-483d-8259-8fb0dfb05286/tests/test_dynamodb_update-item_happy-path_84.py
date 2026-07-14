from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_sets_new_attribute(cli, ddb_client):
    ddb_client.create_table(
        TableName="Products",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="Products",
        Item={"pk": {"S": "item1"}, "status": {"S": "pending"}},
    )

    result = cli(
        "dynamodb", "update-item",
        "--table-name", "Products",
        "--key", '{"pk":{"S":"item1"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )
    assert result.returncode == 0

    resp = ddb_client.get_item(
        TableName="Products",
        Key={"pk": {"S": "item1"}},
    )
    item = resp.get("Item")
    assert item is not None
    assert item["status"]["S"] == "active"