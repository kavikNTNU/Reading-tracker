# Learning Notes — Reading Tracker API

Notes from building a small FastAPI + Pydantic in-memory book-tracking API.

## FastAPI structure

- `app = FastAPI()` creates the application object.
- A plain `def` is just a normal Python function — nothing special happens
  until you decorate it.
- `@app.get("/path")`, `@app.post("/path")`, etc. register the function
  right below them as the handler for that method + path. Only decorated
  functions are reachable over HTTP; undecorated helper functions are not.
- Whatever a route function returns is serialized straight to JSON.

## Pydantic models (`book.py`)

- A `class Book(BaseModel)` describes the *shape of data*, not behavior —
  fields and types, e.g. `title: str`, `pages: int`.
- FastAPI uses the model both to validate incoming request bodies and to
  shape outgoing responses.
- `id: Optional[int] = None` lets a client POST a book without supplying
  an id, while the server fills it in before storing.

## Shared in-memory state

- `books: list[Book] = []` and `next_id = 1` live at module level in
  `main.py`, so every route function (which all share the module's scope)
  can read and mutate the same list/counter.
- Because there's no database, this state resets every time the server
  restarts.

## The `global` keyword gotcha

- Python decides at compile time whether a name inside a function is
  local, based on whether the function ever *assigns* to it.
- `next_id += 1` inside a function is an assignment, so without
  `global next_id` declared **inside that function**, Python treats
  `next_id` as a new local variable — and reading it before the
  (nonexistent) local is assigned raises:
  `UnboundLocalError: cannot access local variable 'next_id' where it is
  not associated with a value`.
- Declaring `global next_id` at module level does nothing — the
  declaration only matters inside the function that mutates the name.
- Mutating an *attribute* of a passed-in object (e.g. `book.id = next_id`)
  does not require `global`, since it's not rebinding the name `book`.

## Avoiding duplicated lookup logic

- `get_book`, `update_book`, and `delete_book` all originally looped over
  `books` looking for a matching id. Factored into one helper:

  ```python
  def find_book(book_id: int) -> tuple[int, Book]:
      for index, book in enumerate(books):
          if book.id == book_id:
              return index, book
      raise HTTPException(status_code=404, detail="Book not found")
  ```

- Callers that only need the book use `_, book = find_book(book_id)`;
  callers that need to mutate the list use `index, _ = find_book(book_id)`.
  The underscore is the Python convention for "value intentionally
  unused."

## HTTP status codes used

- `201 Created` — returned by `POST /books` on success.
- `404 Not Found` — raised via `HTTPException` when a `book_id` doesn't
  exist.
- `204 No Content` — returned by `DELETE /books/{id}`; a 204 response
  should have **no body**, so the handler returns nothing (`None`)
  rather than a confirmation dict.

## Testing the API

- Python's equivalent of `console.log` is `print()` — output shows up in
  the terminal running `uvicorn`, not in the HTTP response.
- Easiest interactive testing: start the server, then open
  `http://127.0.0.1:8000/docs` for FastAPI's auto-generated Swagger UI
  (try requests, see status codes and bodies, no extra tools needed).
- Also testable via `curl` or a Python script using `requests`.

## Running the server

Two ways to invoke it, depending on whether the venv is activated:

```
# venv activated in this terminal (venv\Scripts\Activate.ps1 already run —
# prompt shows "(venv)"): just use the bare command
python -m uvicorn main:app --reload --port 8000

# venv NOT activated: call the venv's python.exe directly by path instead
./venv/Scripts/python.exe -m uvicorn main:app --reload --port 8000
```

Both run the same interpreter/uvicorn in the end. Using the full path
works whether or not the venv is activated; the bare `python` command
only works once `(venv)` is showing in the prompt — otherwise it may
resolve to a different Python install (or none at all).

- `--reload` restarts the server automatically when source files change.
- The terminal running this command must stay open and untouched — typing
  another command into it (or closing the tab) kills the server, which
  then shows as `ERR_CONNECTION_REFUSED` in the browser even though
  nothing about the code is wrong.
