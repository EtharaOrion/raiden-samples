from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_put_get_chain_number_key(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_cpgnk1",
                 "--attribute-definitions", '[{"AttributeName":"id","AttributeType":"N"}]',
                 "--key-schema", '[{"AttributeName":"id","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Tbl_cpgnk1" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cpgnk1",
                 "--item", '{"id":{"N":"1000"},"name":{"S":"kilo"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_cpgnk1",
                 "--key", '{"id":{"N":"1000"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_cpgnk1", Key={"id": {"N": "1000"}})
    assert from_item(resp["Item"]) == {"id": 1000, "name": "kilo"}
