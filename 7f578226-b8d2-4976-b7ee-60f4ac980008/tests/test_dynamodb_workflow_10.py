from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_composite_key_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl8",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "WfTbl8" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl8",
                 "--item", '{"pk":{"S":"p1"},"sk":{"S":"s1"},"v":{"N":"9"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl8", Key={"pk": {"S": "p1"}, "sk": {"S": "s1"}})
    assert resp["Item"]["v"]["N"] == "9"
