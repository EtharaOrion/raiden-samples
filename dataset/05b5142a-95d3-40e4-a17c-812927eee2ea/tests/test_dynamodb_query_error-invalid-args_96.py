from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_required_table_name(cli, ddb_client):
    result = cli("dynamodb", "query", "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"abc"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr or "usage" in result.stderr.lower() or "the following arguments are required" in result.stderr.lower()