from fastapi import FastAPI, HTTPException
from book import Book


app = FastAPI()

books: list[Book] = []   # <-- the list lives here, shared across all requests
next_id = 1

#print("Hello world test0")
@app.get("/")
def read_root():
    #print("Hello world test")
    return {"Hello": "World"}

@app.get("/books")       # new endpoint to view the list
def get_books():
    return books

def find_book(book_id: int) -> tuple[int, Book]:
    for index, book in enumerate(books):
        if book.id == book_id:
            return index, book
    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/books", status_code=201)      # new endpoint to add to the list
def add_book(book: Book):
    global next_id
    book.id = next_id
    next_id += 1
    books.append(book)
    return book

@app.get("/books/{book_id}")   # new endpoint to view a single book
def get_book(book_id: int):
    # for book in books:
    #         if book.id == book_id:
    #             return book
    #     raise HTTPException(status_code=404, detail="Book not found")
    _, book = find_book(book_id)
    return book

@app.put("/books/{book_id}")   # new endpoint to update a book
def update_book(book_id: int, updated_book: Book):
    # for index, book in enumerate(books):
    #             if book.id == book_id:
    #                 updated_book.id = book_id  # Ensure the ID remains the same
    #                 books[index] = updated_book
    #                 return updated_book
    #         raise HTTPException(status_code=404, detail="Book not found")
    index, _ = find_book(book_id)
    updated_book.id = book_id  # Ensure the ID remains the same
    books[index] = updated_book
    return updated_book

@app.delete("/books/{book_id}", status_code=204)   # new endpoint to delete a book
def delete_book(book_id: int):
    # for index, book in enumerate(books):
    #             if book.id == book_id:
    #                 del books[index]
    #                 return {"detail": "Book deleted"}
    #         raise HTTPException(status_code=404, detail="Book not found")
    index, _ = find_book(book_id)
    del books[index]

