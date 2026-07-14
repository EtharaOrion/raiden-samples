from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_condition_attribute_not_exists_success(cli, ddb_client):
    table_name = "CondPutTable"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    result = cli(
        "dynamodb", "put-item",
        "--table-name", table_name,
        "--item", '{"id":{"S":"k1"},"v":{"S":"first"}}',
        "--condition-expression", "attribute_not_exists(id)",
    )
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName=table_name, Key={"id": {"S": "k1"}})
    item = resp.get("Item")
    assert item is not None
    assert item["v"] == {"S": "first"}