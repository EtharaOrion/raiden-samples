from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_heterogeneous_types_roundtrip(cli, ddb_client):
    table = "HeteroTable"
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
    stored = resp.get("Item")
    assert stored is not None
    assert stored["id"] == {"S": "k1"}
    assert stored["count"] == {"N": "42"}
    assert stored["live"] == {"BOOL": True}
    assert stored["tags"] == {"L": [{"S": "a"}, {"S": "b"}]}