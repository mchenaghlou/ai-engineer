# Concurrency in Python for AI Engineering (Async Mental Model)

This document explains Python async concurrency from a practical AI engineering perspective. The goal is to build a usable mental model for systems like LLM orchestration, retrieval pipelines, and API-heavy services.

---

# 1. Concurrency Model (Mental Model)

Python async is based on a **single-threaded event loop**.

At any instant, only one piece of Python code executes. However, execution can switch between tasks when a task is waiting on I/O.

This is different from:

- Multithreading (OS-level scheduling)
- Multiprocessing (true parallel execution across CPU cores)

Async provides **concurrency**, not parallelism.

## Concurrency vs Parallelism

- **Concurrency:** multiple tasks make progress over time (interleaved execution)
- **Parallelism:** multiple tasks execute at the same time (true simultaneous execution)

Python async = concurrency only.

## Why async exists

AI systems are dominated by I/O latency:

- LLM API calls
- Vector database queries
- HTTP requests
- File I/O

Without async, one slow call blocks everything.

## Non-blocking execution

Non-blocking means:

- A task yields control when waiting
- The event loop runs other tasks during that wait

No preemption exists. Everything is cooperative.

---

# 2. async/await Basics (Language Layer)

Async Python is built on **coroutines**.

A coroutine is a function that can pause and resume execution.

## async def (coroutine definition)

```python
async def fetch_data():
    return 42
```

### Meaning

- Defines a coroutine function
- Does NOT execute immediately
- Returns a coroutine object when called

## await (suspension point)

The `await` keyword:

- pauses execution of the coroutine
- returns control to the event loop
- resumes when result is ready

### Example

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

## Key idea

When execution hits `await`:

- coroutine pauses
- event loop switches tasks
- resumes later

## Coroutines vs normal functions

- Normal function: runs immediately to completion
- Coroutine: pauses and resumes via `await`

## Chaining async calls

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

Execution is sequential async, not concurrent.

---

# 3. Event Loop + Task Scheduling (Core Engine)

The **event loop** is the scheduler.

It repeatedly:

- picks a ready task
- runs it until `await`
- stores state
- switches to another task

## Coroutines vs Tasks

- **Coroutine:** defined function, not running
- **Task:** scheduled coroutine executing in event loop

## create_task

```python
asyncio.create_task(coroutine)
```

Meaning:

- schedules coroutine immediately
- allows independent execution
- returns a Task object

## Example: concurrent workers

```python
import asyncio

async def worker(name):
    print(f"{name} started")
    await asyncio.sleep(2)
    print(f"{name} finished")

async def main():
    t1 = asyncio.create_task(worker("A"))
    t2 = asyncio.create_task(worker("B"))

    await t1
    await t2

asyncio.run(main())
```

## Execution timeline

```
t=0s
A started
B started

t=0–2s
A sleeping
B sleeping

t=2s
A finished
B finished
```

---

# 4. Running Concurrency (AI Engineering Pattern)

## Fan-out / Fan-in pattern

- Fan-out: start multiple async tasks
- Fan-in: collect results

## asyncio.gather

```python
import asyncio

async def call_llm(prompt):
    await asyncio.sleep(1)
    return f"response to {prompt}"

async def main():
    prompts = ["hello", "world", "ai", "systems"]

    results = await asyncio.gather(
        *(call_llm(p) for p in prompts)
    )

    print(results)

asyncio.run(main())
```

## gather behavior

- runs all tasks concurrently
- waits for all to complete
- returns results in input order

## Execution model

```
t=0s: all tasks start

t=1s: all tasks complete
```

---

# 5. Blocking vs Non-blocking + Thread Escape Hatch

Async only works for **I/O-bound work**.

## Blocking CPU work

```python
import time

def cpu_task():
    time.sleep(2)
    return "done"
```

This blocks the event loop.

## run_in_executor

```python
import asyncio
import time

def blocking_io():
    time.sleep(2)
    return "blocking result"

async def main():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, blocking_io)
    print(result)

asyncio.run(main())
```

## Meaning

- moves blocking work to thread pool
- keeps event loop responsive
- preserves concurrency

## Practical rule

- async → I/O orchestration
- threads → blocking libraries
- processes → CPU-heavy workloads

---

# Final Mental Model

The async event loop is a **scheduler for waiting tasks**, not a parallel execution engine.

Execution progresses only when:

- a task is ready
- or a task is waiting

Everything else is scheduling mechanics.
