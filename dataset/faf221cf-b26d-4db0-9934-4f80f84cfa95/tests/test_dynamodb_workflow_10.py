from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import from_item


def test_workflow_multi_put_get_each(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfMulti1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for i in range(3):
        result = cli("dynamodb", "put-item", "--table-name", "WfMulti1",
                     "--item", '{"pk":{"S":"m%d"},"n":{"N":"%d"}}' % (i, i))
        assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "WfMulti1",
                 "--key", '{"pk":{"S":"m1"}}')
    assert result.returncode == 0
    present = ddb_client.get_item(TableName="WfMulti1", Key={"pk": {"S": "m0"}})
    assert "Item" in present
    gone = ddb_client.get_item(TableName="WfMulti1", Key={"pk": {"S": "m1"}})
    assert "Item" not in gone
    still = ddb_client.get_item(TableName="WfMulti1", Key={"pk": {"S": "m2"}})
    assert still["Item"]["n"] == {"N": "2"}
