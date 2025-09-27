# Backend Test Suite

This directory contains comprehensive unit and integration tests for the Restaurant Checkout System backend API.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py             # Shared pytest fixtures and configuration
├── test_models.py          # SQLAlchemy model tests
├── test_schemas.py         # Pydantic schema validation tests
├── test_repository.py      # Repository layer tests
├── test_api.py            # API endpoint tests
└── test_integration.py    # End-to-end integration tests
```

## Test Categories

### 1. Model Tests (`test_models.py`)
- **Purpose**: Test SQLAlchemy database models
- **Coverage**: 
  - Model creation and validation
  - Relationships between models
  - Database constraints
  - Foreign key relationships
  - Default values and nullable fields

### 2. Schema Tests (`test_schemas.py`)
- **Purpose**: Test Pydantic schemas for request/response validation
- **Coverage**:
  - Valid schema creation
  - Validation error handling
  - Field constraints (positive prices, valid dates)
  - Optional field handling
  - JSON serialization

### 3. Repository Tests (`test_repository.py`)
- **Purpose**: Test database operations and business logic
- **Coverage**:
  - CRUD operations for all entities
  - Order creation with validation
  - Payment data handling and security
  - Error handling for invalid data
  - Database transaction management

### 4. API Tests (`test_api.py`)
- **Purpose**: Test FastAPI endpoints
- **Coverage**:
  - All GET, POST endpoints
  - HTTP status codes
  - Request/response formats
  - Error responses (404, 400, 422)
  - Admin endpoints
  - CORS functionality

### 5. Integration Tests (`test_integration.py`)
- **Purpose**: Test complete workflows end-to-end
- **Coverage**:
  - Complete order workflow (menu → cart → checkout)
  - Menu browsing scenarios
  - Error handling workflows
  - Large order processing
  - Concurrent order simulation
  - Payment data security

## Key Test Fixtures

### Database Fixtures
- **`db`**: Fresh database session for each test
- **`client`**: FastAPI test client with test database
- **`setup_test_data`**: Pre-populated test data (categories and items)

### Sample Data Fixtures
- **`sample_category_data`**: Template category data
- **`sample_item_data`**: Template item data  
- **`sample_order_data`**: Template order with payment info

## Running Tests

```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_api.py -v
pytest tests/test_repository.py -v

# Run with coverage
pytest tests/ --cov=checkout --cov-report=term-missing

# Run only unit tests (exclude integration)
pytest tests/ -k "not integration"

# Run only integration tests
pytest tests/test_integration.py
```

### Test Options
```bash
# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific test method
pytest tests/test_api.py::TestAPIEndpoints::test_create_order_success

# Generate HTML coverage report
pytest --cov=checkout --cov-report=html
```

## Test Coverage Goals

Our test suite aims for comprehensive coverage:

- **Models**: 95%+ coverage of all database models
- **Repository**: 100% coverage of all repository functions  
- **API Endpoints**: 100% coverage of all routes
- **Error Handling**: All error conditions tested
- **Business Logic**: All validation and calculation logic covered

## Test Data Management

### Test Database
- Uses SQLite in-memory database for speed
- Fresh database created for each test function
- Automatic cleanup after each test

### Test Data Strategy
- Minimal fixtures for fast test execution
- Self-contained tests with their own data setup
- Realistic test data that mirrors production scenarios

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```bash
# CI command
pytest tests/ --cov=checkout --cov-report=xml --junitxml=test-results.xml
```

## Test Best Practices

### Writing New Tests
1. **Arrange-Act-Assert pattern**: Set up data, perform action, verify result
2. **Descriptive test names**: `test_create_order_with_invalid_item_should_return_400`
3. **One assertion per test**: Focus each test on a single behavior
4. **Use fixtures**: Reuse common setup code via pytest fixtures
5. **Test edge cases**: Invalid inputs, boundary conditions, error scenarios

### Mock Usage
- Database operations use real test database for integration testing
- External services should be mocked (payment processors, etc.)
- Network calls should be mocked in unit tests

### Performance Considerations
- Tests should complete in < 30 seconds total
- Use in-memory database for speed
- Minimal test data for faster execution
- Parallel test execution where possible

## Debugging Failed Tests

### Common Issues
1. **Database state**: Ensure tests clean up properly
2. **Test isolation**: Each test should be independent
3. **Async operations**: Ensure proper async/await usage
4. **Fixtures scope**: Check fixture scope matches test requirements

### Debug Commands
```bash
# Run with pdb debugger
pytest --pdb tests/test_api.py::TestAPIEndpoints::test_create_order_success

# Verbose output with print statements
pytest -v -s tests/test_repository.py

# Show local variables on failure
pytest --tb=long tests/
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all existing tests pass
3. Add new tests for new functionality
4. Update this README if adding new test categories
5. Maintain >90% test coverage

## Dependencies

### Test Framework
- **pytest**: Main testing framework
- **pytest-asyncio**: Async test support

### Database Testing  
- **SQLAlchemy**: ORM with test database support
- **SQLite**: In-memory database for testing

### Coverage and Reporting
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities (if needed)

---

For questions about the test suite, see the main project README or contact the development team.
