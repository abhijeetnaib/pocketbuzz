# PocketBuzz Test Suite

This directory contains comprehensive tests for the PocketBuzz backend.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_ai_engine.py        # AI content generation tests
├── test_analyzer.py         # Sales analytics tests
├── test_campaigns_api.py    # Campaign API endpoint tests
├── test_integration.py      # End-to-end integration tests
├── test_parser.py           # POS report parsing tests
├── test_webhook.py          # WhatsApp webhook tests
└── test_whatsapp.py         # WhatsApp messaging tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_ai_engine.py
```

### Run tests with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run only unit tests
```bash
pytest -m unit
```

### Run only integration tests
```bash
pytest -m integration
```

### Run with verbose output
```bash
pytest -v
```

## Test Coverage

The test suite covers:

### 1. **AI Engine** (`test_ai_engine.py`)
- Caption generation for different campaign types
- Image generation with cultural accuracy
- Visual prompt generation for Indian dishes
- JPEG format enforcement for WhatsApp compatibility
- Fallback mechanisms when APIs fail

### 2. **WhatsApp Integration** (`test_whatsapp.py`)
- Campaign blast to multiple recipients
- Single message sending
- Phone number cleaning and formatting
- Notification sending with magic links
- Payload construction
- Error handling and resilience

### 3. **Campaign API** (`test_campaigns_api.py`)
- Campaign creation (manual and AI-generated)
- Campaign approval flow
- Campaign sending
- Image regeneration
- Campaign listing and filtering
- Target audience selection
- Data validation

### 4. **WhatsApp Webhook** (`test_webhook.py`)
- Webhook verification
- Incoming message handling
- Auto-reply functionality
- Menu loading for AI context
- Different message types
- AI fallback mechanisms
- Error handling

### 5. **Integration Tests** (`test_integration.py`)
- Complete campaign lifecycle (create → approve → send)
- Image regeneration workflow
- Multiple campaign management
- Delivery tracking
- Error recovery
- Authentication flow
- Database operations

### 6. **Sales Analyzer** (`test_analyzer.py`)
- Bestseller detection
- Slow day identification
- Churn prediction
- Dead stock analysis

### 7. **POS Parser** (`test_parser.py`)
- Phone number extraction and cleaning
- Record validation
- Aggregator filtering (Zomato/Swiggy)
- Email parsing

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `mock_restaurant_id`: Test restaurant ID
- `mock_campaign_data`: Sample campaign data
- `mock_customer_phones`: Test phone numbers
- `mock_menu`: Sample menu data

## Mocking Strategy

Tests use `unittest.mock` to mock:
- External API calls (OpenAI, Fal.ai, WhatsApp)
- Database operations (Supabase)
- HTTP clients (httpx)

This ensures tests are:
- Fast (no real API calls)
- Reliable (no network dependencies)
- Isolated (no side effects)

## Writing New Tests

When adding new tests:

1. **Use descriptive names**: `test_send_campaign_to_multiple_recipients`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Mock external dependencies**: Don't make real API calls
4. **Test edge cases**: Empty inputs, errors, failures
5. **Use fixtures**: Reuse common test data
6. **Add docstrings**: Explain what the test validates

Example:
```python
@pytest.mark.asyncio
async def test_send_campaign_success(mock_customer_phones):
    """Test that campaigns are successfully sent to all recipients."""
    # Arrange
    with patch('app.services.whatsapp.send_single_message') as mock_send:
        mock_send.return_value = True
        
        # Act
        result = await send_campaign_blast(
            restaurant_id="test",
            phones=mock_customer_phones,
            image_url="https://example.com/test.jpg",
            caption="Test"
        )
        
        # Assert
        assert result["sent"] == len(mock_customer_phones)
        assert result["failed"] == 0
```

## Continuous Integration

These tests should be run:
- Before every commit
- In CI/CD pipeline
- Before deployments

## Test Data

Test data should:
- Use realistic Indian restaurant scenarios
- Include edge cases (special characters, long text, etc.)
- Cover all campaign types (BEST_SELLER, SLOW_DAY, etc.)
- Test with actual Indian dish names (Wada Pav, Chicken Malvani, etc.)
