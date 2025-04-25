"""Tests for the formatters."""
import json
import pytest
import csv
import io
from typing import Dict, List, Any

from ..formatters.factory import FormatterFactory
from ..formatters.text import TextFormatter
from ..formatters.json import JSONFormatter
from ..formatters.csv import CSVFormatter
from ..core.exceptions import FormattingError


# Sample test data
SAMPLE_RESULT = {
    "columns": ["id", "period", "customer", "amount", "credit_limit", "revenue_relevant", "account_type", "account_description"],
    "rows": [
        (1, "2020/01", "Musterdebitor Gewo GmbH", 1000.0, 700.0, "Nein", "Ist", "Debitor"),
        (2, "2020/02", "Musterdebitor Gewo GmbH", -500.0, 700.0, "Ja", "Ist", "Debitor"),
        (3, "2020/03", "Musterdebitor Gewo GmbH", 2000.0, 700.0, "Nein", "Ist", "Debitor"),
    ],
    "affected_rows": 3,
    "execution_time": 0.05,
    "query": "SELECT * FROM transactions WHERE customer = 'Musterdebitor Gewo GmbH'"
}

SAMPLE_ERROR = ValueError("Invalid query: Table 'nonexistent' does not exist")


@pytest.mark.asyncio
async def test_formatter_factory():
    """Test the formatter factory."""
    # Test creating formatters
    text_formatter = FormatterFactory.create("text")
    json_formatter = FormatterFactory.create("json")
    csv_formatter = FormatterFactory.create("csv")
    
    assert isinstance(text_formatter, TextFormatter)
    assert isinstance(json_formatter, JSONFormatter)
    assert isinstance(csv_formatter, CSVFormatter)
    
    # Test unsupported formatter
    with pytest.raises(FormattingError):
        FormatterFactory.create("unsupported")
    
    # Test available formats
    available_formats = FormatterFactory.get_available_formats()
    assert "text" in available_formats
    assert "json" in available_formats
    assert "csv" in available_formats


@pytest.mark.asyncio
async def test_text_formatter():
    """Test the text formatter."""
    formatter = TextFormatter()
    
    # Test formatting result
    formatted = await formatter.format(SAMPLE_RESULT)
    assert isinstance(formatted, str)
    assert "Musterdebitor" in formatted
    assert "1000.0" in formatted
    assert "-500.0" in formatted
    assert "2000.0" in formatted
    
    # Test formatting error
    error_formatted = await formatter.format_error(SAMPLE_ERROR)
    assert isinstance(error_formatted, str)
    assert "Invalid query" in error_formatted
    
    # Test formatting None
    none_formatted = await formatter.format(None)
    assert "No results" in none_formatted
    
    # Test formatting empty list
    empty_formatted = await formatter.format([])
    assert "No results" in empty_formatted


@pytest.mark.asyncio
async def test_json_formatter():
    """Test the JSON formatter."""
    formatter = JSONFormatter()
    
    # Test formatting result
    formatted = await formatter.format(SAMPLE_RESULT)
    assert isinstance(formatted, str)
    
    # Verify it's valid JSON
    parsed = json.loads(formatted)
    assert "columns" in parsed
    assert "rows" in parsed
    assert "affected_rows" in parsed
    assert "execution_time" in parsed
    assert "query" in parsed
    
    # Test formatting error
    error_formatted = await formatter.format_error(SAMPLE_ERROR)
    assert isinstance(error_formatted, str)
    
    # Verify error JSON
    error_parsed = json.loads(error_formatted)
    assert "error" in error_parsed
    assert "Invalid query" in error_parsed["error"]
    
    # Test formatting None
    none_formatted = await formatter.format(None)
    none_parsed = json.loads(none_formatted)
    assert "result" in none_parsed
    assert none_parsed["result"] is None
    
    # Test formatting empty list
    empty_formatted = await formatter.format([])
    empty_parsed = json.loads(empty_formatted)
    assert "result" in empty_parsed
    assert empty_parsed["result"] == []


@pytest.mark.asyncio
async def test_csv_formatter():
    """Test the CSV formatter."""
    formatter = CSVFormatter()
    
    # Test formatting result
    formatted = await formatter.format(SAMPLE_RESULT)
    assert isinstance(formatted, str)
    
    # Verify it's valid CSV
    csv_file = io.StringIO(formatted)
    reader = csv.reader(csv_file)
    rows = list(reader)
    
    # Check header row
    assert len(rows) > 0
    assert rows[0] == SAMPLE_RESULT["columns"]
    
    # Check data rows
    assert len(rows) == len(SAMPLE_RESULT["rows"]) + 1  # +1 for header
    
    # Test formatting error
    error_formatted = await formatter.format_error(SAMPLE_ERROR)
    assert isinstance(error_formatted, str)
    
    # Verify error CSV
    error_csv = io.StringIO(error_formatted)
    error_reader = csv.reader(error_csv)
    error_rows = list(error_reader)
    assert len(error_rows) == 2  # Header + error message
    assert error_rows[0] == ["error"]
    assert "Invalid query" in error_rows[1][0]
    
    # Test formatting None
    none_formatted = await formatter.format(None)
    none_csv = io.StringIO(none_formatted)
    none_reader = csv.reader(none_csv)
    none_rows = list(none_reader)
    assert len(none_rows) == 2  # Header + message
    assert none_rows[0] == ["message"]
    assert "No results" in none_rows[1][0]
    
    # Test formatting empty list
    empty_formatted = await formatter.format([])
    empty_csv = io.StringIO(empty_formatted)
    empty_reader = csv.reader(empty_csv)
    empty_rows = list(empty_reader)
    assert len(empty_rows) == 2  # Header + message
    assert empty_rows[0] == ["message"]
    assert "No results" in empty_rows[1][0] 