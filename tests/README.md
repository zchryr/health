# Postman API Tests

This directory contains Postman collection tests for the health API service. The tests verify the functionality of both PyPI and NPM package information endpoints.

## Prerequisites

- Node.js (v14 or higher)
- npm (comes with Node.js)

## Installing Newman

Newman is a command-line collection runner for Postman. To install it globally:

```bash
npm install -g newman
```

## Running the Tests

To run all tests in the collection:

```bash
newman run postman_collection.json
```

### Running with Environment Variables

If you need to run the tests against a different environment (e.g., staging or production), you can use environment variables:

```bash
newman run postman_collection.json -e environment.json
```

### Running with Reporters

Newman supports various reporters. Here are some common options:

1. CLI reporter (default):
```bash
newman run postman_collection.json -r cli
```

2. JSON reporter:
```bash
newman run postman_collection.json -r json --reporter-json-export report.json
```

3. HTML reporter (requires additional installation):
```bash
npm install -g newman-reporter-htmlextra
newman run postman_collection.json -r htmlextra --reporter-htmlextra-export report.html
```

## Test Collection Structure

The collection contains tests for:

### PyPI Package Tests
- Individual package tests (requests, boto3, aiobotocore, etc.)
- Batch package information endpoint

### NPM Package Tests
- Individual package tests (lodash, chalk, request, etc.)
- Batch package information endpoint

## Test Coverage

The tests verify:
- HTTP status codes
- Response format and structure
- Package metadata accuracy
- Repository information
- Version information
- Error handling

## Troubleshooting

If you encounter any issues:

1. Ensure the API server is running on `localhost:8002`
2. Check that Newman is properly installed: `newman --version`
3. Verify the collection file path is correct
4. Check the API server logs for any backend issues

## Contributing

When adding new tests:
1. Follow the existing test structure
2. Include appropriate assertions
3. Test both success and error cases
4. Update this README if necessary