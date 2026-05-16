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

### Python → JSON and JSON → Python Conversions

Here are the most important built-in functions you’ll use every day as an AI engineer:

1. Convert Python dict → JSON string (json.dumps)
Pythonimport json  # This is Python's built-in JSON library

```
# Python dictionary (what you work with in code)
data = {
    "name": "Alex",
    "age": 28,
    "is_ai_engineer": True,
    "skills": ["Python", "Asyncio", "Pydantic"],
    "favorite_llm": "Grok"
}

# Convert to JSON string (ready to send over the internet)
json_string = json.dumps(data, indent=2)   # indent=2 makes it pretty

print(json_string)
Output:
JSON{
  "name": "Alex",
  "age": 28,
  "is_ai_engineer": true,
  "skills": [
    "Python",
    "Asyncio",
    "Pydantic"
  ],
  "favorite_llm": "Grok"
}
```

### 2. Convert JSON string → Python dict (json.loads)
Python
```
import json

# This is what you usually receive from an API (a string)
json_string = '''
{
  "name": "Alex",
  "age": 28,
  "is_ai_engineer": true,
  "skills": ["Python", "Asyncio", "Pydantic"],
  "favorite_llm": "Grok"
}
'''

# Convert back to Python dictionary
data = json.loads(json_string)

print(type(data))           # <class 'dict'>
print(data["name"])         # Alex
print(data["skills"][0])    # Python
```

### 3. Working with JSON Files (very common)
Python
```
import json

# Save to file
data = {"prompt": "Explain JSON", "model": "grok-beta"}
with open("request.json", "w") as f:
    json.dump(data, f, indent=2)   # write to file

# Load from file
with open("request.json", "r") as f:
    loaded_data = json.load(f)     # note: load (not loads)

print(loaded_data)
```

### 4. Real AI Example – Sending JSON to an API (most common pattern)
Python
```
import requests
import json

payload = {
    "model": "gpt-4o",
    "messages": [
        {"role": "user", "content": "Explain REST and JSON in one sentence"}
    ],
    "temperature": 0.7
}

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY"
    },
    json=payload          # requests automatically does json.dumps for you!
)

print(response.json())    # response.json() does json.loads automatically
```

Pro tip: When using requests, you can just pass json=payload and it handles the conversion for you — no need to call json.dumps manually.
---

# 3. What is REST? – Deep Dive for Beginners

Hey! 👋  

Now that we’ve covered the basics of **HTTP** and **JSON**, it’s time to talk about **REST** — one of the most important concepts you’ll use every single day as an AI engineer.

Don’t worry if it sounds technical at first — I’m going to explain it slowly, clearly, and with real-world examples (including how it relates to AI systems like LLMs, RAG pipelines, and agents). By the end of this section, REST will feel simple and natural.

### What does REST actually stand for?

**REST** = **Representational State Transfer**

It’s **not** a library, a tool, or a programming language.  
It’s an **architectural style** — a set of design rules for building web APIs that are clean, predictable, and easy to use.

The idea was invented by Roy Fielding in the year 2000, and today **almost every major API in the world** (OpenAI, Anthropic, GitHub, Stripe, weather services, your company’s internal tools, etc.) follows REST principles.

### The Core Idea of REST (explained simply)

Instead of thinking about “actions” (like “login”, “calculate score”, or “ask LLM”), REST says:

> “Let’s organise everything around **resources** — the things our system manages.”

A **resource** is anything that can be created, read, updated, or deleted.  
Examples in the AI world:
- A user account
- A document in your knowledge base
- A chat conversation
- An LLM response
- A vector embedding
- An agent’s task or memory

Every resource gets its own unique **URL** (web address).  
You then use the standard **HTTP methods** (GET, POST, PUT, DELETE, etc.) to work with that resource.

That’s the entire philosophy of REST in one sentence:
> **Resources are manipulated using standard HTTP methods.**

### Typical REST Patterns (The Classic CRUD Operations)

Here are the most common patterns you will see in every REST API:

- **`GET /users`**  
  → **List** all users (or all documents, all chats, etc.)

- **`GET /users/123`**  
  → **Retrieve** (get details of) a single user with ID 123

- **`POST /users`**  
  → **Create** a brand new user  
  (You send the user data in the JSON body of the request)

- **`PUT /users/123`**  
  → **Update / Replace** the entire user with ID 123  
  (You send the full new data in the JSON body)

- **`PATCH /users/123`** (optional but very common)  
  → **Partially update** only specific fields of user 123  
  (e.g. just change the email address)

- **`DELETE /users/123`**  
  → **Delete** user number 123

These patterns are called **CRUD**:
- **C**reate → POST
- **R**ead   → GET
- **U**pdate → PUT / PATCH
- **D**elete → DELETE

### Real-World AI Examples

When you use OpenAI’s API, you are actually using REST:

- `POST /v1/chat/completions` → Create a new LLM response (you send your prompt in the JSON body)
- `GET /v1/models` → List all available models

If you build your own RAG (Retrieval-Augmented Generation) system, you might create endpoints like:
- `POST /documents` → Upload a new PDF → the server embeds it and stores it
- `GET /documents` → List all documents in your knowledge base
- `DELETE /documents/abc123` → Remove a document

### Why REST is Perfect for AI Engineers

1. It’s **predictable** — once you learn the pattern, every new API feels familiar.
2. It’s **stateless** — each request contains everything the server needs (no hidden session memory).
3. It works beautifully with **JSON** (the data format we learned earlier).
4. It scales extremely well when you start using **async** HTTP clients like `httpx` to call 10+ APIs at the same time.

### Key Idea (One More Time, Loud and Clear)

> **Resources live at URLs.  
> HTTP methods tell the server what to do with those resources.**

That’s it. No fancy verbs, no custom actions — just clean URLs + standard HTTP methods.

This simple rule is why REST has become the universal language of web APIs.

---

You now have a solid, beginner-friendly understanding of REST!  

This concept will appear in **every** AI system you build — whether you’re calling external LLMs, building your own internal APIs, or connecting to vector databases.

Copy the entire content above into a file called `03-what-is-rest.md` and you’re all set.

Ready for the next section (or want me to expand any part even more)? Just say the word! 🚀
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
