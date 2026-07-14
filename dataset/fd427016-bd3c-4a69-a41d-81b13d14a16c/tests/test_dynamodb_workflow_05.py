from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfTblQ",
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
    for sk in ["s1", "s2", "s3"]:
        result = cli("dynamodb", "put-item", "--table-name", "WfTblQ",
                     "--item", '{"pk":{"S":"grp"},"sk":{"S":"' + sk + '"}}')
        assert result.returncode == 0
    result = cli("dynamodb", "query", "--table-name", "WfTblQ",
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"grp"}}')
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="WfTblQ",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "grp"}},
    )
    got = {from_item(it)["sk"] for it in resp["Items"]}
    assert got == {"s1", "s2", "s3"}
