from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_after_recreate_attempt(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_par1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_par1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode != 0
    assert "ResourceInUseException" in result.stderr
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_par1",
                 "--item", '{"pk":{"S":"pa1"},"v":{"S":"still_works"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_par1", Key={"pk": {"S": "pa1"}})
    assert from_item(resp["Item"]) == {"pk": "pa1", "v": "still_works"}
