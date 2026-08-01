from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_unicode_string_roundtrip(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_uni1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_uni1",
                 "--item", '{"pk":{"S":"uni1"},"txt":{"S":"cafe latte"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_uni1", Key={"pk": {"S": "uni1"}})
    assert from_item(resp["Item"]) == {"pk": "uni1", "txt": "cafe latte"}
