from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_heterogeneous_types_roundtrip(cli, ddb_client):
    ddb_client.create_table(
        TableName="HetTbl",
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "put-item",
        "--table-name", "HetTbl",
        "--item", '{"id":{"S":"k1"},"count":{"N":"42"},"live":{"BOOL":true},"tags":{"L":[{"S":"a"},{"S":"b"}]}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="HetTbl", Key={"id": {"S": "k1"}})
    item = resp.get("Item")
    assert item is not None
    assert item["id"] == {"S": "k1"}
    assert item["count"] == {"N": "42"}
    assert item["live"] == {"BOOL": True}
    assert item["tags"] == {"L": [{"S": "a"}, {"S": "b"}]}