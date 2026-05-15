# Basics of HTTP, REST, and JSON – A Friendly Beginner’s Guide for Future AI Engineers

Hey there!

Welcome to your very first steps into the world of **HTTP, REST, and JSON**. Don’t worry if these words sound completely new — this is a structured introduction from first principles with practical Python usage.

By the end of this file you will understand:
- What HTTP is
- How request/response communication works
- What REST is and how APIs are structured around it
- What JSON is and how it is used for data exchange
- Basic usage in Python with `requests`

This knowledge is foundational for AI engineering because most AI systems interact with external services through HTTP APIs using REST and JSON.

---

## 1. What is HTTP?

**HTTP (HyperText Transfer Protocol)** is the communication protocol used between clients and servers on the web.

Conceptually, it is a request-response system:

- Client sends a **request**
- Server returns a **response**

Example interaction:

> Client: GET https://example.com

> Server: 200 OK + response data

HTTP is stateless: each request is independent of previous ones.

---

## 2. Core components of an HTTP request

Every HTTP request typically includes:

### Method
Defines the action:
- GET → retrieve data
- POST → create data
- PUT → update data
- DELETE → remove data

### URL
The endpoint being accessed:
```
https://api.example.com/users/123
```

### Headers
Metadata about the request:
- Authentication tokens
- Content type (e.g., JSON)

Example:
```
Content-Type: application/json
Authorization: Bearer <token>
```

### Body (optional)
Payload sent to the server (commonly used in POST/PUT)

---

## 3. What is REST?

**REST (Representational State Transfer)** is an architectural style for designing APIs.

REST organizes systems around **resources**, each identified by a URL.

Typical REST patterns:

- GET /users → list users
- GET /users/123 → retrieve user
- POST /users → create user
- PUT /users/123 → update user
- DELETE /users/123 → delete user

Key idea:

Resources are manipulated using standard HTTP methods.

---

## 4. What is JSON?

**JSON (JavaScript Object Notation)** is a lightweight data format used for exchanging structured data.

Example JSON object:

```json
{
  "name": "Alex",
  "age": 28,
  "is_ai_engineer": true,
  "skills": ["Python", "Asyncio", "Pydantic"],
  "favorite_llm": "Grok"
}
```

Mapping to Python:
- Object → dict
- Array → list
- String/Number/Boolean → native types

JSON is the default format for most modern APIs.

---

## 5. Basic HTTP in Python (GET request)

Using the `requests` library:

```python
import requests

response = requests.get("https://httpbin.org/get")

print("Status code:", response.status_code)

data = response.json()
print("Response:", data)
```

Key points:
- `.get()` sends HTTP GET request
- `.status_code` shows result (200 = success)
- `.json()` converts JSON response into Python dictionary

---

## 6. Sending data with POST

POST is used to send structured data (usually JSON).

```python
import requests

payload = {
    "prompt": "Explain HTTP in one sentence",
    "max_tokens": 50
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(
    "https://httpbin.org/post",
    json=payload,
    headers=headers
)

print("Status:", response.status_code)
print("Response:", response.json())
```

Important detail:
- `json=payload` automatically serializes Python dict → JSON

---

## 7. Why this matters for AI engineering

Almost every AI system depends on HTTP APIs:

- Calling LLMs (OpenAI, Anthropic, etc.)
- Querying vector databases
- Fetching external data (search, weather, finance)
- Connecting microservices

Everything is built on:

**HTTP + REST + JSON**

Once you understand this layer, you can integrate any AI service or API.

---

## Quick recap

- HTTP → communication protocol (request/response)
- REST → API design pattern based on resources
- JSON → standard data format for APIs

In Python, `requests` is the simplest way to interact with HTTP APIs.

---

End of document.
