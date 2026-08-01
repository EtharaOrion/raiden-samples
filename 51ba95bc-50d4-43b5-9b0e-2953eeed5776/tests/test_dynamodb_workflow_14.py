from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_numeric_pk_lifecycle(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_numpk1",
                 "--attribute-definitions", '[{"AttributeName":"id","AttributeType":"N"}]',
                 "--key-schema", '[{"AttributeName":"id","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_numpk1",
                 "--item", '{"id":{"N":"42"},"label":{"S":"answer"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_numpk1", Key={"id": {"N": "42"}})
    assert from_item(resp["Item"]) == {"id": 42, "label": "answer"}
