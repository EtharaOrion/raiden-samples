from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_composite_partial_key_get_absent(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_cpk1",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cpk1",
                 "--item", '{"pk":{"S":"p"},"sk":{"S":"s1"},"v":{"S":"x"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_cpk1",
                               Key={"pk": {"S": "p"}, "sk": {"S": "s2"}})
    assert "Item" not in resp
    resp2 = ddb_client.get_item(TableName="Tbl_cpk1",
                                Key={"pk": {"S": "p"}, "sk": {"S": "s1"}})
    assert from_item(resp2["Item"]) == {"pk": "p", "sk": "s1", "v": "x"}
