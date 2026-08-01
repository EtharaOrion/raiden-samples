from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_put_get_readback(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf1Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Wf1Tbl" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Wf1Tbl",
                 "--item", '{"pk":{"S":"a1"},"n":{"N":"5"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf1Tbl", Key={"pk": {"S": "a1"}})
    assert from_item(resp["Item"]) == {"pk": "a1", "n": 5}
