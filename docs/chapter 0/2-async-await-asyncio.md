# Concurrency in Python for AI Engineering
## Building a Real Mental Model for `asyncio`

> **Goal:** Not to memorize syntax, but to understand what the runtime is actually doing.

This document explains Python async concurrency from a practical AI engineering perspective. The focus is on building a working mental model that you can apply to real systems.

---

## Context: Why Async Matters

Most AI systems today are **heavily I/O-bound**. They spend most of their time waiting:

- ⏳ Waiting for LLM APIs (OpenAI, Claude, local models)
- ⏳ Waiting for vector databases (Pinecone, Weaviate, Milvus)
- ⏳ Waiting for Redis lookups
- ⏳ Waiting for HTTP services
- ⏳ Waiting for file I/O or streaming data
- ⏳ Waiting for database queries

**Async exists primarily to make waiting efficient.**

Without async, one slow API call blocks your entire application. With async, you can start multiple requests and let them overlap in their waiting periods.

---

# Part 1: The Core Mental Model

## What is an Event Loop?

Python async is based on something called an **event loop**.

**The event loop is a scheduler.** Its job is to manage many tasks that spend most of their time waiting on external systems.

### Key Insight

> **Async Python is usually single-threaded.**

Even though many tasks appear to run "at the same time", only one piece of Python code is actually executing at any instant.

The illusion of simultaneity comes from tasks constantly pausing and resuming.

```
Time ──────────────────────────────>

Task A: |run  |wait for API.........|resume |done|
Task B:       |run |wait for DB.........|resume|done|
Task C:                |run|wait for file........|done|

Only one "run" box executes at a time.
The "wait" boxes don't block others.
```

---

## Concurrency vs Parallelism

These two terms are often confused. Let's be precise.

### Concurrency

**Multiple tasks make progress over time** (interleaved execution).

```
Example:
- Task A starts
- Task A waits on an API (pauses)
- Task B runs meanwhile
- Task B waits on a database (pauses)
- Task A resumes (API response ready)
- Task A finishes
- Task B resumes (database response ready)
- Task B finishes
```

Tasks are interleaved. They are not literally executing simultaneously.

### Parallelism

**Multiple tasks are literally executing at the same time** (simultaneous execution).

This usually requires:
- Multiple CPU cores
- Multiple processes
- Multiple threads

**Async Python itself does NOT provide parallel execution.** It provides efficient coordination of waiting tasks.

### For AI Engineering

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Concurrency (async)** | I/O-bound work | Multiple LLM API calls |
| **Parallelism (threads)** | Blocking I/O | Database drivers that don't support async |
| **Parallelism (processes)** | CPU-heavy work | Vector quantization, embedding computation |

---

# Part 2: First Async Example

Let's start with the simplest possible async program:

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "data"

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
```

Output:
```
data
```

Now let's go through this line by line.

---

# Part 3: Line-by-Line Breakdown

## `import asyncio`

```python
import asyncio
```

This imports Python's async framework. `asyncio` provides:

- The event loop
- Task scheduling
- Async utilities
- Coroutine support

Think of it as the runtime system for async execution.

---

## `async def fetch_data():`

```python
async def fetch_data():
    await asyncio.sleep(1)
    return "data"
```

This defines a **coroutine function**.

### Key Difference: async vs regular functions

| Aspect | Regular Function | Async Function |
|--------|------------------|----------------|
| **Definition** | `def foo():` | `async def foo():` |
| **Execution** | Runs immediately when called | Does NOT run immediately |
| **Return value** | Result directly | Coroutine object |
| **Resumable** | No | Yes (via `await`) |

### What happens when you call it

```python
# Regular function
x = fetch_data()  # Runs immediately, x = "data" (after 1 second)

# Async function
x = fetch_data()  # Does NOT run yet
                  # x is a coroutine object that says:
                  # "Here is some async work that can be executed later."
```

The coroutine waits for something to tell the event loop to execute it.

---

## `await asyncio.sleep(1)`

```python
await asyncio.sleep(1)
```

This is the most important line in async Python.

### `asyncio.sleep(1)`

This creates an async operation that completes after 1 second.

**Unlike `time.sleep(1)`, it does NOT block the thread.** That's the whole point.

### `await`

The `await` keyword means:

> **Pause this coroutine until the result is ready.**

### What Happens at `await`

```
1. Coroutine pauses
2. Its state is saved (local variables, instruction pointer)
3. Control returns to the event loop
4. Event loop can run something else
5. (1 second later) sleep completes
6. Coroutine resumes exactly where it stopped
7. Execution continues
```

This is called **non-blocking** because the thread doesn't freeze. The event loop stays responsive.

---

## `return "data"`

After the sleep completes, execution resumes and returns `"data"`.

So eventually:
```python
await fetch_data()
```

produces:
```python
"data"
```

---

## `async def main():`

```python
async def main():
    result = await fetch_data()
    print(result)
```

This defines another coroutine. In real applications, this is usually the orchestration layer that coordinates other async operations.

---

## `result = await fetch_data()`

This does several things:

```python
fetch_data()        # Creates a coroutine object
await ...           # Executes it (suspends until done)
```

Execution enters `fetch_data()`. Inside, `await asyncio.sleep(1)` pauses. After 1 second, `return "data"` runs. Finally, `result = "data"`.

---

## `asyncio.run(main())`

```python
asyncio.run(main())
```

This is the entry point.

**This line creates and starts the event loop.**

Without this line, nothing executes. It's the glue between the sync world and the async world.

---

# Part 4: Sequential Async vs Concurrent Async

Here's a critical distinction that trips up many beginners.

## Sequential Async Example

```python
import asyncio

async def step1():
    await asyncio.sleep(1)
    return "A"

async def step2(prev):
    await asyncio.sleep(1)
    return prev + "B"

async def main():
    a = await step1()
    b = await step2(a)
    print(b)

asyncio.run(main())
```

**Execution flow:**

```
t=0s: Enter main()
t=0s: Enter step1()
t=0s: Hit 'await asyncio.sleep(1)' in step1() → PAUSE
t=1s: Resume step1()
t=1s: Return "A"
t=1s: a = "A"
t=1s: Enter step2("A")
t=1s: Hit 'await asyncio.sleep(1)' in step2() → PAUSE
t=2s: Resume step2()
t=2s: Return "AB"
t=2s: b = "AB"
t=2s: Print "AB"

Total time: 2 seconds
```

### Important Observation

This program takes about **2 seconds** because the operations happen one after another.

Even though the code is async, nothing overlaps.

This is called **sequential async execution**.

> **Async syntax alone does NOT create concurrency.**
>
> Concurrency only happens when multiple tasks are scheduled together.

---

# Part 5: Real Concurrency with `create_task()`

Now we get to the magic.

`create_task()` is the key that unlocks real async concurrency.

## Example

```python
import asyncio

async def worker(name: str):
    print(f"{name} started")
    await asyncio.sleep(2)
    print(f"{name} finished")

async def main():
    # Create two independent tasks that can run concurrently
    t1 = asyncio.create_task(worker("A"))
    t2 = asyncio.create_task(worker("B"))

    # Wait for both tasks to complete
    await t1
    await t2

asyncio.run(main())
```

**Output:**
```
A started
B started
A finished
B finished
```

**Total time: ~2 seconds, not 4 seconds.**

---

## What `create_task()` Actually Does

Here's the critical line:

```python
asyncio.create_task(worker("A"))
```

This line does **NOT wait for the coroutine to finish**.

Compare:

```python
await worker("A")        # ← Blocks until worker("A") completes

asyncio.create_task(worker("A"))  # ← Returns immediately, runs in background
```

### Three Things Happen Behind the Scenes

1. **Wrapping:** The coroutine gets wrapped inside a Task object (asyncio's way of managing background work)
2. **Scheduling:** The event loop immediately schedules that task to run
3. **Non-blocking:** Your code continues executing the very next line—no waiting

**Think of it like this:**

```
await worker("A"):
  "I'm going to stand here and wait until A finishes
   before I even think about starting B."

create_task(worker("A")):
  "Start A right now, hand me a ticket (the Task),
   and while A is doing its thing, I'm going to go
   ahead and start B too."
```

---

## Execution Timeline

```
t=0s:
  ├─ A started
  ├─ B started
  └─ (both hit await asyncio.sleep(2) → PAUSE)

t=0s to t=2s:
  ├─ A waiting
  └─ B waiting
     (tasks can't run; event loop waits for external events)

t=2s:
  ├─ A finished
  └─ B finished
```

**Total: ~2 seconds**

This is actual async concurrency. The waiting periods overlap perfectly.

---

# Part 6: The Most Important Async Insight

## Core Principle

> **Async performance comes from overlapping waiting periods — not from making your code run any faster.**

That one sentence is the entire secret behind why asyncio feels like magic.

### What Async Is NOT

- ❌ NOT about speeding up CPU computation
- ❌ NOT about making your code execute faster
- ❌ NOT a replacement for multithreading when you have heavy computation

### What Async IS

✅ **About one simple but incredibly powerful idea: Stop wasting time while you're waiting.**

### The Reality of Modern Applications

In almost every real-world program (especially AI systems), most of the time is spent waiting:

```
Your code's actual time budget:

Running:  |███████████|  ~5%  (actual execution)
Waiting:  |████████████████████████████████████████████████|  ~95%
```

In normal synchronous code, when you wait for one thing, the entire program sits there doing nothing.

With asyncio, you can say:
> "Start waiting for this API... but while you're waiting, go ahead and start waiting for these other APIs too."

All those waiting periods overlap. The total wall-clock time approaches the longest single wait.

### Example: AI RAG Pipeline

```python
# Sequential (3 + 2 + 1.5 = 6.5 seconds)
result1 = await vector_db.search(query)       # 3s
result2 = await llm.call(result1)              # 2s
result3 = await rerank(result2)                # 1.5s

# Concurrent (max(3, 2, 1.5) = 3 seconds)
r1 = asyncio.create_task(vector_db.search(query))
r2 = asyncio.create_task(llm.call(query))
r3 = asyncio.create_task(rerank(candidates))
result1, result2, result3 = await r1, await r2, await r3
```

**2x speedup from just overlapping waits.**

---

# Part 7: `asyncio.gather()` — The Fan-Out/Fan-In Pattern

Once you understand `create_task()`, the next most useful pattern is `asyncio.gather()`.

## What is Fan-Out/Fan-In?

- **Fan-Out:** Launch many async tasks at once
- **Fan-In:** Collect all their results

This pattern is incredibly common in AI systems.

## Example

```python
import asyncio

async def call_llm(prompt: str):
    await asyncio.sleep(1)  # Pretend this is a real LLM API call
    return f"response to '{prompt}'"

async def main():
    prompts = [
        "What is AI?",
        "Explain async",
        "Tell me a joke"
    ]

    # Fan-out: Launch all at once
    results = await asyncio.gather(
        *(call_llm(p) for p in prompts)
    )

    # Fan-in: Collect results
    print(results)

asyncio.run(main())
```

**Output:**
```python
[
    "response to 'What is AI?'",
    "response to 'Explain async'",
    "response to 'Tell me a joke'"
]
```

**Time: ~1 second (not 3 seconds)**

---

## How `gather()` Works

### Behind the Scenes

1. **Fan-Out:** `gather()` automatically turns each coroutine into a Task and schedules them all at once
2. **Running:** All tasks run concurrently (with overlapping waits)
3. **Fan-In:** When all complete, `gather()` collects results into a list
4. **Order:** Results are in the same order as input (even if task C finishes before task A)

### The Generator Expression

```python
*(call_llm(p) for p in prompts)
```

This is Python's clean way of saying:
> "Create a coroutine for every prompt and unpack them as separate arguments to gather()."

Equivalent to:
```python
asyncio.gather(
    call_llm("What is AI?"),
    call_llm("Explain async"),
    call_llm("Tell me a joke")
)
```

---

## Real AI Use Cases

`gather()` appears constantly in real AI systems:

| Use Case | Pattern |
|----------|---------|
| Multiple LLMs (different models, same prompt) | `gather(*[model.call(prompt) for model in models])` |
| Batch embeddings | `gather(*[embed(doc) for doc in docs])` |
| Parallel retrieval | `gather(vec_db.search(q), keyword_search(q), ...))` |
| Agent coordination | `gather(*[agent.run() for agent in agents])` |
| API data fetching | `gather(*[fetch_from_api(url) for url in urls])` |
| Scoring candidates | `gather(*[score(candidate) for candidate in candidates])` |

---

# Part 8: Why Async Fails with CPU Work

Async only helps with **waiting**.

It does NOT help with heavy CPU computation.

## Example: Blocking CPU Work

```python
import time

def cpu_task():
    """This is synchronous blocking work."""
    total = 0
    for i in range(100_000_000):  # Heavy computation
        total += i
    return total
```

### What Happens

```python
result = cpu_task()  # Blocks the entire thread for ~2 seconds
                     # During those 2 seconds:
                     # - event loop freezes
                     # - ALL async tasks stop progressing
                     # - system is unresponsive
```

### Why It's a Problem

In an async application, if one coroutine calls blocking CPU work, it blocks all other coroutines. This defeats the entire purpose of async.

---

## Solution: `run_in_executor()`

If you must do blocking work, move it to a thread pool:

```python
import asyncio
import time

def cpu_task():
    """Heavy computation."""
    total = 0
    for i in range(100_000_000):
        total += i
    return total

async def main():
    loop = asyncio.get_running_loop()
    
    # Move blocking work to thread pool
    result = await loop.run_in_executor(None, cpu_task)
    
    print(f"Result: {result}")

asyncio.run(main())
```

**What happens:**

1. The blocking function runs in a separate thread
2. The event loop stays responsive
3. Other async tasks can continue
4. When the thread finishes, the coroutine resumes

---

## Rule of Thumb

| Type of Work | Tool | Reason |
|-------------|------|--------|
| **I/O operations** (network, files, databases) | `asyncio` | Waiting doesn't block; concurrency is efficient |
| **Blocking I/O** (legacy libraries) | `run_in_executor()` + threading | Offload to thread pool; keeps event loop responsive |
| **CPU-heavy work** | `multiprocessing` or distributed | Need true parallelism across cores |

---

# Part 9: Building Your Mental Model

## The Event Loop is a Traffic Controller

Think of the event loop as a traffic controller managing coroutines at an intersection:

```
Event Loop (Traffic Controller)
├─ Task A: Run until 'await'
├─ (Task A hits await → pauses)
├─ Task B: Run until 'await'
├─ (Task B hits await → pauses)
├─ Task C: Run until 'await'
├─ (Task C hits await → pauses)
│
└─ (Check if any task is ready to resume)
   └─ (Task A's wait completed → resume Task A)
   └─ Task A: Run until 'await' or 'return'
   └─ (Repeat)
```

## State Machine for a Coroutine

Every coroutine cycles through these states:

```
┌─────────────────────────────────────────┐
│                                         │
│   ┌─────────────────────────────┐      │
│   │                             │      │
│   └──> [RUNNING] ──await──> [PAUSED]  │
│                    ↓              ↓    │
│            (some other task runs)  │    │
│                    ↓              ↓    │
│   ┌─────────────────────────────┐      │
│   │ (condition met: ready to    │      │
│   │  resume)                    │      │
│   └─────────────────────────────┘      │
│                                         │
│   └──> [RUNNING] ──return──> [DONE]   │
│                                         │
└─────────────────────────────────────────┘
```

---

## Key Patterns

### Pattern 1: Sequential Async
```python
result = await task1()
result = await task2(result)
```
**Use when:** Second task depends on first task's result.

### Pattern 2: Concurrent with `create_task()`
```python
t1 = asyncio.create_task(task1())
t2 = asyncio.create_task(task2())
r1, r2 = await t1, await t2
```
**Use when:** Fine-grained control, specific ordering needed.

### Pattern 3: Fan-Out/Fan-In with `gather()`
```python
results = await asyncio.gather(
    *(task(x) for x in items)
)
```
**Use when:** Many independent tasks, results needed in same order.

### Pattern 4: Offload Blocking Work
```python
result = await loop.run_in_executor(None, blocking_func)
```
**Use when:** Must call non-async blocking code.

---

# Part 10: Final Mental Model Summary

## The Core Insight

```
The async event loop is a SCHEDULER for waiting tasks.
It's NOT a parallel execution engine.

Execution progresses in two ways:

1. A task is ready to run (has new work)
2. A task was waiting and the condition is now met
```

## Three Key Ideas

### 1. Coroutines Pause at `await`

```python
async def task():
    print("A")           # Runs immediately
    await wait()         # ← Pauses here
    print("B")           # Runs after wait completes
```

### 2. Event Loop Schedules Waiting Tasks

```python
async def main():
    t1 = create_task(task1())  # Schedule task1
    t2 = create_task(task2())  # Schedule task2
    # Both run concurrently (not the same thing as parallel)
    await t1
    await t2
```

### 3. Concurrency Means Overlapped Waits

```
Without async:
Task A wait (2s) → Task B wait (2s) → Total 4s

With async:
Task A wait (2s) ─┐
Task B wait (2s) ─┤ → Total ~2s (overlapped)
```

---

## For AI Engineers: Why This Matters

Your typical AI pipeline looks like:

```
User Query
    ↓
[LLM Call - wait 1.5s]
    ↓
[Vector Search - wait 0.5s]
    ↓
[Rerank - wait 0.3s]
    ↓
[Format Response - 0.01s]
```

**Sequential:** 1.5 + 0.5 + 0.3 + 0.01 = **2.31 seconds per request**

**With async concurrency:** ~max(1.5, 0.5, 0.3) = **~1.5 seconds per request**

**At scale (1000 concurrent requests):**
- Sequential: Can handle ~430 requests/second
- Async: Can handle ~667 requests/second (55% improvement)

This is why async is critical for production AI systems.

---

## Next Steps

You now understand:

✅ How the event loop schedules coroutines  
✅ The difference between concurrency and parallelism  
✅ How `await` pauses and resumes execution  
✅ How `create_task()` enables true concurrency  
✅ How `gather()` provides fan-out/fan-in patterns  
✅ Why async fails with CPU work  

Practice these patterns in your own code:

1. Convert a sequential I/O pipeline to async
2. Use `gather()` to parallelize batch operations
3. Build a simple concurrent API call system

Then, explore async libraries for your domain:
- `aiohttp` for HTTP requests
- `motor` for MongoDB
- `asyncpg` for PostgreSQL
- `anthropic` (async client) for Claude API
- `openai` (async client) for OpenAI API

The mental model you've built applies to all of them.

---

**Happy async coding!** 🚀
