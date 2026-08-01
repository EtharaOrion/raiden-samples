from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_heterogeneous_types_roundtrip(cli, ddb_client):
    table = "HetTypesTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    item = '{"id":{"S":"k1"},"count":{"N":"42"},"live":{"BOOL":true},"tags":{"L":[{"S":"a"},{"S":"b"}]}}'
    result = cli("dynamodb", "put-item", "--table-name", table, "--item", item)
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName=table, Key={"id": {"S": "k1"}})
    got = resp.get("Item")
    assert got is not None
    assert got["id"] == {"S": "k1"}
    assert got["count"] == {"N": "42"}
    assert got["live"] == {"BOOL": True}
    assert got["tags"] == {"L": [{"S": "a"}, {"S": "b"}]}