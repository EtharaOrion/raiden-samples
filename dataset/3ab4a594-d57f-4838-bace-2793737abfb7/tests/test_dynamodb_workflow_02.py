from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf3Tbl",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    for sk in ["a", "b", "c"]:
        result = cli("dynamodb", "put-item", "--table-name", "Wf3Tbl",
                     "--item", '{"pk":{"S":"P1"},"sk":{"S":"' + sk + '"}}')
        assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "Wf3Tbl",
                 "--item", '{"pk":{"S":"P2"},"sk":{"S":"z"}}')
    assert result.returncode == 0

    resp = ddb_client.query(
        TableName="Wf3Tbl",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "P1"}})
    from _ddb_http import from_item
    got = set(from_item(it)["sk"] for it in resp["Items"])
    assert got == {"a", "b", "c"}
