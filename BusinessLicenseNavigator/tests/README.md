# Business License Navigator - Test Suite

This directory contains the comprehensive test suite for the Business License Navigator system.

## 📁 Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── README.md               # This file
├── run_tests.py            # Main test runner
├── test_config.py          # Test configuration and utilities
├── test_integration.py     # Integration tests
├── test_delaware_rag.py    # Delaware RAG tests
├── test_delaware_mcp.py    # Delaware MCP tests
└── test_generic_system.py  # Generic system tests
```

## 🧪 Test Categories

### 1. **Unit Tests** (`--unit`)
Tests individual components in isolation:
- Agent module imports
- StateHandler functionality
- BusinessTypeHandler functionality
- MCPFactory functionality

### 2. **Delaware Tests** (`--delaware`)
Tests Delaware-specific functionality:
- Delaware RAG server
- Delaware MCP server
- Delaware-specific queries

### 3. **Generic System Tests** (`--generic`)
Tests the generic multi-state system:
- Generic state detection
- Generic industry detection
- Dynamic state creation
- Generic RAG server
- Generic MCP server
- Generic agent queries

### 4. **Integration Tests** (`--integration`)
Tests the complete system integration:
- End-to-end query processing
- Configuration validation
- Module imports
- Streamlit app functionality

## 🚀 Running Tests

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Specific Test Categories
```bash
# Unit tests only
python tests/run_tests.py --unit

# Delaware tests only
python tests/run_tests.py --delaware

# Generic system tests only
python tests/run_tests.py --generic

# Integration tests only
python tests/run_tests.py --integration
```

### Run Individual Test Files
```bash
# Run specific test file
python tests/test_generic_system.py

# Run Delaware RAG tests
python tests/test_delaware_rag.py

# Run Delaware MCP tests
python tests/test_delaware_mcp.py

# Run integration tests
python tests/test_integration.py
```

## 📊 Test Output

The test runner provides detailed output including:

- **Test Progress**: Real-time progress indicators
- **Success/Failure Status**: Clear pass/fail indicators
- **Error Details**: Detailed error messages for failed tests
- **Performance Metrics**: Test duration and timing
- **Summary Report**: Overall test results summary

### Example Output
```
🚀 Business License Navigator - Complete Test Suite
============================================================

📋 Running Unit Tests...
✅ Agent module imported successfully
✅ StateHandler imported and initialized successfully
✅ BusinessTypeHandler imported and initialized successfully
✅ MCPFactory imported and initialized successfully

📋 Running Delaware Tests...
✅ Delaware RAG tests passed
✅ Delaware MCP tests passed

📋 Running Generic System Tests...
✅ Generic state detection test passed
✅ Generic industry detection test passed
✅ Generic agent queries test passed

📋 Running Integration Tests...
✅ Integration tests passed

============================================================
📊 Test Results Summary
============================================================
✅ Passed: 12
❌ Failed: 0
⏱️  Duration: 15.23 seconds

🎉 All tests passed! The system is ready to use.
```

## 🔧 Test Configuration

The `test_config.py` file contains:

- **Test Settings**: Timeout values, retry attempts, log levels
- **Test Data**: Predefined test queries and expected results
- **Test Fixtures**: State configurations and business type data
- **Utility Functions**: Helper functions for test validation
- **Test Logger**: Consistent logging across all tests

## 📝 Writing New Tests

### Adding Unit Tests
1. Create a new test function in the appropriate test file
2. Use the `TestLogger` for consistent output
3. Follow the naming convention: `test_<component_name>()`
4. Add the test to the test runner if needed

### Example Test Function
```python
def test_new_component():
    """Test new component functionality."""
    logger = TestLogger("New Component")
    
    try:
        # Test logic here
        result = some_function()
        
        if expected_condition:
            logger.success("Test passed")
            return True
        else:
            logger.error("Test failed")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        return False
```

### Adding Integration Tests
1. Add test cases to `test_integration.py`
2. Test end-to-end functionality
3. Validate system behavior with real queries
4. Test configuration and setup

## 🐛 Debugging Tests

### Common Issues
1. **Import Errors**: Ensure parent directory is in Python path
2. **Timeout Errors**: Increase timeout in `test_config.py`
3. **Qdrant Connection**: Tests may fail if Qdrant server is not running
4. **API Key Issues**: Ensure environment variables are set

### Debug Mode
Run tests with verbose output:
```bash
python -v tests/run_tests.py
```

### Individual Test Debugging
```bash
# Run specific test with detailed output
python -c "
import sys
sys.path.append('.')
from tests.test_generic_system import test_generic_state_detection
test_generic_state_detection()
"
```

## 📈 Test Coverage

The test suite covers:

- ✅ **Core Components**: Agent, handlers, factories
- ✅ **State Management**: State detection, configuration
- ✅ **Business Logic**: Industry detection, license matching
- ✅ **RAG Systems**: Delaware and generic RAG servers
- ✅ **MCP Systems**: Delaware and generic MCP servers
- ✅ **Integration**: End-to-end query processing
- ✅ **Configuration**: JSON config validation
- ✅ **Error Handling**: Exception handling and fallbacks

## 🔄 Continuous Integration

The test suite is designed to work with CI/CD systems:

- **Exit Codes**: Proper exit codes for CI systems
- **Timeout Protection**: Prevents hanging tests
- **Clean Output**: Structured output for CI parsing
- **Modular Design**: Can run specific test categories

## 📋 Test Maintenance

### Regular Tasks
1. **Update Test Data**: Keep test queries current
2. **Add New States**: Update state configurations
3. **Add New Industries**: Update business type patterns
4. **Performance Monitoring**: Track test execution times
5. **Coverage Analysis**: Ensure new features are tested

### Best Practices
- Keep tests independent and isolated
- Use descriptive test names
- Include both positive and negative test cases
- Test edge cases and error conditions
- Maintain test data consistency
- Document test purpose and expected behavior 