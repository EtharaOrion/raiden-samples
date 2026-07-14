from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_delete_one(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfTblQDel",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for sk in ["r1", "r2", "r3"]:
        result = cli("dynamodb", "put-item", "--table-name", "WfTblQDel",
                     "--item", '{"pk":{"S":"g"},"sk":{"S":"' + sk + '"}}')
        assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "WfTblQDel",
                 "--key", '{"pk":{"S":"g"},"sk":{"S":"r2"}}')
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="WfTblQDel",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "g"}},
    )
    got = {from_item(it)["sk"] for it in resp["Items"]}
    assert got == {"r1", "r3"}
