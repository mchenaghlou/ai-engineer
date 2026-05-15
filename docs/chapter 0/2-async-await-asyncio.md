# Concurrency in Python for AI Engineering
## Building a Real Mental Model for `asyncio`

This document explains Python async concurrency from a practical AI engineering perspective. The goal is not to memorize syntax. The goal is to understand what the runtime is actually doing when you write async Python.

Most AI systems today are heavily I/O-bound. They spend most of their time waiting:

- waiting for LLM APIs
- waiting for vector databases
- waiting for Redis
- waiting for HTTP services
- waiting for files
- waiting for streams

Async exists primarily to make waiting efficient.

---

# 1. The Core Mental Model

Python async is based on something called an **event loop**.

The event loop is basically a scheduler. Its job is to manage many tasks that spend most of their time waiting on external systems.

The important thing to understand is this:

> Async Python is usually single-threaded.

Even though many tasks appear to run "at the same time", only one piece of Python code is actually executing at any instant.

The illusion of simultaneity comes from tasks constantly pausing and resuming.

---

# 2. Concurrency vs Parallelism

These two terms are often confused.

## Concurrency

Concurrency means multiple tasks make progress over time.

Example:

- Task A starts
- Task A waits on an API
- Task B runs meanwhile
- Task B waits on a database
- Task A resumes

The tasks are interleaved.

They are not literally executing simultaneously.

---

## Parallelism

Parallelism means multiple tasks are literally executing at the same time.

This usually requires:

- multiple CPU cores
- multiple processes
- multiple threads

Async Python itself does NOT provide parallel execution.

It provides efficient coordination of waiting tasks.

---

# 3. Why Async Matters in AI Engineering

AI systems are dominated by latency.

Imagine a pipeline like this:

```text
User Request
    ↓
LLM API Call
    ↓
Vector Search
    ↓
Redis Lookup
    ↓
Another LLM Call
    ↓
Streaming Response
```

Most of the runtime is not CPU computation.

Most of the runtime is:

```text
waiting...
waiting...
waiting...
waiting...
```

Without async, every wait blocks the entire program.

With async, the system can work on other requests while one request is waiting.

That is the entire value proposition.

---

# 4. First Async Example

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

Now let us go through this line by line.

---

# 5. Line-by-Line Explanation

## `import asyncio`

```python
import asyncio
```

This imports Python's async framework.

`asyncio` provides:

- the event loop
- task scheduling
- async utilities
- coroutine support

Think of it as the runtime system for async execution.

---

## `async def fetch_data():`

```python
async def fetch_data():
```

This defines a **coroutine function**.

An `async def` function behaves differently from a normal function.

A normal function executes immediately when called.

An async function does NOT execute immediately.

Instead, calling it creates a coroutine object.

Example:

```python
x = fetch_data()
```

This does NOT run the function body yet.

It creates a coroutine object that says:

> "Here is some async work that can be executed later."

---

## `await asyncio.sleep(1)`

```python
await asyncio.sleep(1)
```

This is the most important line in async Python.

### `asyncio.sleep(1)`

This creates an async operation that completes after 1 second.

Unlike `time.sleep(1)`, it does NOT block the thread.

---

### `await`

The `await` keyword means:

> Pause this coroutine until the result is ready.

When execution reaches `await`:

1. the coroutine pauses
2. its state is saved
3. control returns to the event loop
4. the event loop runs something else

Later, when the sleep completes, the coroutine resumes exactly where it stopped.

---

## `return "data"`

```python
return "data"
```

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
```

This defines another coroutine.

This is usually the orchestration layer of the application.

---

## `result = await fetch_data()`

```python
result = await fetch_data()
```

This line does several things.

First:

```python
fetch_data()
```

creates a coroutine object.

Then:

```python
await ...
```

actually executes it.

Execution enters `fetch_data()`.

Inside `fetch_data()`:

```python
await asyncio.sleep(1)
```

pauses the coroutine for 1 second.

After the second completes:

```python
return "data"
```

runs.

Finally:

```python
result = "data"
```

---

## `print(result)`

```python
print(result)
```

Outputs:

```text
data
```

---

## `asyncio.run(main())`

```python
asyncio.run(main())
```

This is the entry point.

This line creates and starts the event loop.

Without this line, nothing executes.

---

# 6. Sequential Async vs Concurrent Async

Now let us examine this example carefully.

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

Many beginners assume this runs concurrently.

It does not.

This is still sequential execution.

---

# 7. Understanding the Execution Flow

Execution begins here:

```python
asyncio.run(main())
```

The event loop starts and executes `main()`.

## First Line Inside `main`

```python
a = await step1()
```

Execution enters:

```python
step1()
```

Inside `step1()`:

```python
await asyncio.sleep(1)
```

pauses for 1 second.

After 1 second:

```python
return "A"
```

runs.

Now:

```python
a = "A"
```

---

## Second Line Inside `main`

```python
b = await step2(a)
```

Now execution enters:

```python
step2("A")
```

Inside `step2()`:

```python
await asyncio.sleep(1)
```

pauses another second.

After resuming:

```python
return prev + "B"
```

becomes:

```python
return "AB"
```

Now:

```python
b = "AB"
```

---

## Final Output

```python
print(b)
```

prints:

```text
AB
```

---

# 8. Important Observation

This program takes about:

```text
2 seconds
```

Because the operations happen one after another.

Even though the code is async, nothing overlaps.

This is called:

> sequential async execution

Async syntax alone does NOT create concurrency.

Concurrency only happens when multiple tasks are scheduled together.

---

# 9. Real Concurrency with create_task

Hey there! We've spent the last few sections getting comfortable with the basics of asyncio — coroutines, `await`, and the event loop. Now it's time to see what asyncio is *really* all about: **actual concurrency**.

This is the moment where things start to feel magical. Up until now, your async code has still been running one thing after another (just with nicer syntax). But with `create_task()`, we finally unlock true overlapping execution — the kind of concurrency that makes asyncio shine for real-world applications like AI systems, APIs, and anything that waits on external services.

Let’s look at a simple but powerful example together:

```python
import asyncio

async def worker(name: str):
    print(f"{name} started")
    await asyncio.sleep(2)  # Simulate real work like calling an API or LLM
    print(f"{name} finished")

async def main():
    # Create two independent tasks that can run concurrently
    t1 = asyncio.create_task(worker("A"))
    t2 = asyncio.create_task(worker("B"))

    # Wait for both tasks to complete
    await t1
    await t2

asyncio.run(main())
Go ahead and run this code. What do you see?
textA started
B started
A finished
B finished
```

The entire program finishes in roughly 2 seconds, not 4 seconds. That’s not a typo or a trick — that’s real concurrency happening right in front of you.
Here’s what’s actually going on under the hood. 

When you call asyncio.create_task(worker("A")), you’re not just calling the function. You’re telling the event loop:
“Hey, take this coroutine and schedule it as an independent task. Let it run on its own timeline, alongside anything else that’s happening.”
The moment that line executes, the event loop wraps the coroutine in a Task object and immediately starts running it in the background. It doesn’t pause or wait for worker("A") to finish before moving on to the next line. That’s why t2 gets created almost instantly, and both workers begin their work at the same time.

Inside each worker, the code runs until it hits await asyncio.sleep(2). At that point, each task politely tells the event loop, “I’m going to be waiting for 2 seconds — you can go do other useful work while I’m paused.” Because both tasks are paused at the exact same time, the waiting periods overlap perfectly.

This is the core idea behind asyncio concurrency: tasks run independently and their waiting periods can happen simultaneously. Without create_task(), if you had simply written await worker("A") followed by await worker("B"), the second worker would not even start until the first one completely finished — giving you a total of 4 seconds.

create_task() is the key that unlocks real parallelism for I/O-bound work. It turns your sequential-looking code into something that can juggle multiple operations at once, all managed efficiently by a single thread and the event loop.

This pattern is exactly what makes asyncio so powerful for modern applications — whether you’re calling multiple LLMs in parallel, fetching data from several APIs, or coordinating agents. Once you start thinking in terms of independent tasks, you’ll see opportunities for concurrency everywhere.

Play around with this example before moving on. Try adding a third task, changing the sleep times, or even replacing the sleep with a real network call. Feel how the total runtime stays close to the longest individual wait instead of adding up all the waits.

You’ve just taken your first real step into true async concurrency — and it only gets more exciting from here!

---

# 10. What `create_task()` Actually Does

Hey! Now that you’ve seen `create_task()` in action in the previous section, let’s slow down and look *exactly* at what that one magical line is doing.

Here’s the line we’re talking about:

```python
asyncio.create_task(worker("A"))
```

At first glance, it looks pretty innocent — just another function call. But this single line is the key that unlocks real concurrency in asyncio.

Here’s the most important thing to understand: this line does NOT wait for the coroutine to finish.

That’s right — unlike a normal await worker("A"), which would pause everything until the worker is completely done, create_task() does something completely different. It tells the event loop:

“Hey, take this coroutine, wrap it up as an independent Task, and schedule it to run on its own. Don’t stop the rest of my code — let it keep going right now.”

As soon as that line executes, three important things happen behind the scenes:

The coroutine worker("A") gets wrapped inside a Task object (this is asyncio’s way of managing background work).

The event loop immediately schedules that task to run as soon as possible.

Your code continues executing the very next line — no waiting, no blocking.

That’s why in our example, both t1 and t2 get created almost instantly, and both workers start printing “started” within a fraction of a second.

Think of it like this:

If you used a plain await, you’re basically saying “I’m going to stand here and wait until A finishes before I even think about starting B.”

With create_task(), you’re saying “Start A right now, hand me a ticket (the Task), and while A is doing its thing, I’m going to go ahead and start B too.”

This is the moment your code truly becomes concurrent. The two tasks are now running independently on the same event loop. Their waiting periods (the await asyncio.sleep(2)) can happen at exactly the same time instead of one after the other.

This tiny change — from await to create_task() + await later — is what turns sequential code into overlapping, efficient async code. It’s the foundation of everything powerful you’ll build with asyncio: parallel LLM calls, multi-agent systems, concurrent API requests, and so much more.

In the next section, we’ll look at the exact timeline of what happens second-by-second so you can see the concurrency in action. But for now, just remember this: create_task() doesn’t run the coroutine immediately in a new thread — it simply tells the event loop to manage it independently so multiple things can make progress together.
You’re really starting to see the power now. Keep going — it only gets better!

---

# 11. Execution Timeline

At time `0s`:

```text
A started
B started
```

Then both hit:

```python
await asyncio.sleep(2)
```

Both tasks pause simultaneously.

At time `2s`:

```text
A finished
B finished
```

The total runtime is about 2 seconds, not 4 seconds.

That is actual async concurrency.

---

# 12. The Most Important Async Insight

Async performance comes from overlapping waiting periods.

Not from faster computation.

Async is not:

```text
"make code faster"
```

Async is:

```text
"avoid wasting time while waiting"
```

---

# 13. `asyncio.gather()` — Fan-Out / Fan-In

This pattern appears constantly in AI systems.

Example:

```python
import asyncio

async def call_llm(prompt):
    await asyncio.sleep(1)
    return f"response to {prompt}"

async def main():
    prompts = ["A", "B", "C"]

    results = await asyncio.gather(
        *(call_llm(p) for p in prompts)
    )

    print(results)

asyncio.run(main())
```

---

# 14. What `gather()` Does

`asyncio.gather()` runs multiple coroutines concurrently and waits for all of them.

This pattern is called:

- fan-out → launch many tasks
- fan-in → collect results

Very common in:

- parallel LLM calls
- retrieval pipelines
- multi-agent systems
- ranking pipelines
- embeddings generation

---

# 15. Why Async Fails with CPU Work

Async only helps with waiting.

It does NOT help with heavy CPU computation.

Example:

```python
import time

def cpu_task():
    time.sleep(5)
```

This blocks the entire thread.

During those 5 seconds:

- the event loop freezes
- all async tasks stop progressing

This is why CPU-heavy workloads usually use:

- multiprocessing
- distributed workers
- GPU execution

not asyncio.

---

# 16. Final Mental Model

The event loop is basically a traffic controller.

Coroutines repeatedly do this:

```text
run
pause
resume
pause
resume
finish
```

The pauses happen at `await`.

While one coroutine waits, another can run.

That is the entire async model.
