from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WFQuerySeed",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    for sk in ("s1", "s2", "s3"):
        result = cli("dynamodb", "put-item", "--table-name", "WFQuerySeed",
                     "--item", '{"pk":{"S":"grp"},"sk":{"S":"' + sk + '"}}')
        assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WFQuerySeed",
                 "--item", '{"pk":{"S":"other"},"sk":{"S":"x"}}')
    assert result.returncode == 0

    resp = ddb_client.query(
        TableName="WFQuerySeed",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "grp"}})
    got = {from_item(i)["sk"] for i in resp["Items"]}
    assert got == {"s1", "s2", "s3"}
