from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_tables_isolated(cli, ddb_client, tmp_path):
    for name in ("Tbl_iso_a", "Tbl_iso_b"):
        result = cli("dynamodb", "create-table", "--table-name", name,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_iso_a",
                 "--item", '{"pk":{"S":"shared"},"src":{"S":"a"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_iso_b", Key={"pk": {"S": "shared"}})
    assert "Item" not in resp
    respA = ddb_client.get_item(TableName="Tbl_iso_a", Key={"pk": {"S": "shared"}})
    assert from_item(respA["Item"]) == {"pk": "shared", "src": "a"}
