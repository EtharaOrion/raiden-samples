from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="TblQuery1",
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
    for sk in ("s1", "s2", "s3"):
        result = cli("dynamodb", "put-item", "--table-name", "TblQuery1",
                     "--item", '{"pk":{"S":"grp"},"sk":{"S":"' + sk + '"}}')
        assert result.returncode == 0

    result = cli("dynamodb", "query", "--table-name", "TblQuery1",
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"grp"}}')
    assert result.returncode == 0

    items = ddb_client.query(
        TableName="TblQuery1",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "grp"}},
    )["Items"]
    from _ddb_http import from_item
    sks = {from_item(it)["sk"] for it in items}
    assert sks == {"s1", "s2", "s3"}
