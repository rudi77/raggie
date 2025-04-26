def test_example(example_fixture):
    """Test that demonstrates using a fixture"""
    assert isinstance(example_fixture, str)
    assert example_fixture == "example data"

def test_simple_assertion():
    """Test that demonstrates a simple assertion"""
    assert 1 + 1 == 2

class TestExample:
    """Example test class to demonstrate pytest class naming pattern."""
    
    def test_method(self):
        """Example test method to demonstrate pytest method naming pattern."""
        expected = "example"
        actual = "example"
        assert actual == expected 