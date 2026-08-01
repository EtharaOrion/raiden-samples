from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_range_items_get_each(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_2ri1",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_2ri1",
                 "--item", '{"pk":{"S":"grp"},"sk":{"S":"a"},"v":{"S":"first"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_2ri1",
                 "--item", '{"pk":{"S":"grp"},"sk":{"S":"b"},"v":{"S":"second"}}')
    assert result.returncode == 0
    ra = ddb_client.get_item(TableName="Tbl_2ri1",
                             Key={"pk": {"S": "grp"}, "sk": {"S": "a"}})
    rb = ddb_client.get_item(TableName="Tbl_2ri1",
                             Key={"pk": {"S": "grp"}, "sk": {"S": "b"}})
    assert from_item(ra["Item"])["v"] == "first"
    assert from_item(rb["Item"])["v"] == "second"
