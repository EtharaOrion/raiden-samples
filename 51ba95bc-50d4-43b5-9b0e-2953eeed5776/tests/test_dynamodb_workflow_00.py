from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_put_get_readback(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_cpgr1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Tbl_cpgr1" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cpgr1",
                 "--item", '{"pk":{"S":"a1"},"n":{"N":"5"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_cpgr1", Key={"pk": {"S": "a1"}})
    assert "Item" in resp
    assert from_item(resp["Item"]) == {"pk": "a1", "n": 5}
