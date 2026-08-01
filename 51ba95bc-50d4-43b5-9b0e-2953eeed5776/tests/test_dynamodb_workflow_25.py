from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_absent_then_put_then_present(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_gapp1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_gapp1", Key={"pk": {"S": "gp1"}})
    assert "Item" not in resp
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_gapp1",
                 "--item", '{"pk":{"S":"gp1"},"v":{"S":"now"}}')
    assert result.returncode == 0
    resp2 = ddb_client.get_item(TableName="Tbl_gapp1", Key={"pk": {"S": "gp1"}})
    assert from_item(resp2["Item"]) == {"pk": "gp1", "v": "now"}
