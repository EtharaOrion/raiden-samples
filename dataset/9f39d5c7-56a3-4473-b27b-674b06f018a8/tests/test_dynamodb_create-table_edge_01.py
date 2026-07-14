from _ddb_http import to_item, from_item, to_av, from_av


def test_create_table_pay_per_request_composite_key(cli, ddb_client):
    result = cli(
        "dynamodb", "create-table",
        "--table-name", "CompositeTbl",
        "--attribute-definitions",
        '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"N"}]',
        "--key-schema",
        '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
        "--billing-mode", "PAY_PER_REQUEST",
    )
    assert result.returncode == 0
    assert "CompositeTbl" in ddb_client.list_tables()["TableNames"]

    ddb_client.put_item(
        TableName="CompositeTbl",
        Item={"pk": {"S": "abc"}, "sk": {"N": "5"}},
    )
    resp = ddb_client.get_item(
        TableName="CompositeTbl",
        Key={"pk": {"S": "abc"}, "sk": {"N": "5"}},
    )
    assert resp.get("Item") is not None
    assert resp["Item"]["pk"]["S"] == "abc"
    assert resp["Item"]["sk"]["N"] == "5"