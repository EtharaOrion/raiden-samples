from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multiple_attributes_item(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_multi1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_multi1",
                 "--item", '{"pk":{"S":"mu1"},"a":{"S":"x"},"b":{"N":"3"},"c":{"BOOL":false}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_multi1", Key={"pk": {"S": "mu1"}})
    assert from_item(resp["Item"]) == {"pk": "mu1", "a": "x", "b": 3, "c": False}
