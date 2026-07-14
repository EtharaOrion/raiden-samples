from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seed(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfQ1",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    for sk in ("s1", "s2", "s3"):
        result = cli("dynamodb", "put-item", "--table-name", "WfQ1",
                     "--item", '{"pk":{"S":"p"},"sk":{"S":"' + sk + '"}}')
        assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WfQ1",
                 "--item", '{"pk":{"S":"other"},"sk":{"S":"x1"}}')
    assert result.returncode == 0

    from _ddb_http import from_item
    items = ddb_client.query(
        TableName="WfQ1",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "p"}},
    )["Items"]
    got = {from_item(i)["sk"] for i in items}
    assert got == {"s1", "s2", "s3"}
