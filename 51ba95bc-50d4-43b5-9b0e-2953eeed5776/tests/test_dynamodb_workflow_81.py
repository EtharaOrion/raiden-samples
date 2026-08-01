from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_chain_create_put_put_get_final(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_ccppg1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_ccppg1",
                 "--item", '{"pk":{"S":"cp1"},"stage":{"S":"draft"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_ccppg1",
                 "--item", '{"pk":{"S":"cp1"},"stage":{"S":"final"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_ccppg1",
                 "--key", '{"pk":{"S":"cp1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_ccppg1", Key={"pk": {"S": "cp1"}})
    assert from_item(resp["Item"]) == {"pk": "cp1", "stage": "final"}
