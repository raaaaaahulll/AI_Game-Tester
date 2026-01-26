# API Contract Documentation

This project includes an OpenAPI 3.0 specification that documents all API endpoints, request/response formats, and schemas.

## Files

- **`openapi.yaml`** - OpenAPI 3.0 specification in YAML format

## Viewing the API Documentation

### Option 1: FastAPI Auto-Generated Docs (Recommended)

FastAPI automatically generates interactive API documentation from your code:

1. Start the backend server:
   ```bash
   cd AI_Game_Testing_System/backend
   python main.py
   ```

2. Open your browser and navigate to:
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **OpenAPI JSON**: http://localhost:8000/openapi.json

### Option 2: External Tools

You can import `openapi.yaml` into various tools:

#### Swagger Editor (Online)
1. Go to https://editor.swagger.io/
2. File → Import File → Select `openapi.yaml`
3. View and test the API interactively

#### Postman
1. Open Postman
2. Import → File → Select `openapi.yaml`
3. Generate a collection with all endpoints

#### Insomnia
1. Open Insomnia
2. Application → Preferences → Data → Import Data → From File
3. Select `openapi.yaml`

#### VS Code Extensions
- **OpenAPI (Swagger) Editor**: Provides syntax highlighting and validation
- **REST Client**: Test API endpoints directly from VS Code

## Using the Specification

### Generate Client Code

You can generate client code for various languages using tools like:

- **OpenAPI Generator**: https://openapi-generator.tech/
  ```bash
  openapi-generator generate -i openapi.yaml -g javascript -o ./generated-client
  ```

- **Swagger Codegen**: https://swagger.io/tools/swagger-codegen/

### Validate the Specification

```bash
# Using swagger-cli (npm)
npm install -g @apidevtools/swagger-cli
swagger-cli validate openapi.yaml

# Using openapi-validator (Python)
pip install openapi-validator
openapi-validator openapi.yaml
```

## Specification Details

The OpenAPI specification includes:

- **5 API Endpoints**:
  - `POST /api/start-test` - Start testing session
  - `POST /api/stop-test` - Stop testing session
  - `GET /api/metrics` - Get all metrics
  - `GET /api/status` - Get system status
  - `GET /` - Health check

- **Request/Response Schemas**: Complete type definitions for all endpoints
- **Examples**: Request/response examples for each endpoint
- **Error Responses**: Documented error formats (400, 500)
- **Enums**: Valid values for genre, status, and algorithm fields

## Integration with FastAPI

FastAPI automatically generates OpenAPI documentation from your Python code using:
- Pydantic models for request/response validation
- Type hints for parameter types
- Docstrings for descriptions

The standalone `openapi.yaml` file serves as:
- A design document
- A contract for frontend developers
- A source for client code generation
- Version-controlled API documentation

## Updating the Specification

When adding new endpoints:

1. Add the endpoint to `backend/api.py`
2. Update `openapi.yaml` to reflect the new endpoint
3. Ensure request/response models match the OpenAPI schema
4. Validate the updated specification

## Notes

- The API currently has no authentication (security section is prepared but commented out)
- CORS is enabled for all origins in development mode
- All endpoints return JSON
- Error responses follow FastAPI's standard format: `{"detail": "error message"}`

