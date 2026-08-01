from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_composite_key_lifecycle(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_comp1",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"N"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Tbl_comp1" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_comp1",
                 "--item", '{"pk":{"S":"p1"},"sk":{"N":"10"},"data":{"S":"hello"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_comp1",
                               Key={"pk": {"S": "p1"}, "sk": {"N": "10"}})
    assert from_item(resp["Item"]) == {"pk": "p1", "sk": 10, "data": "hello"}
