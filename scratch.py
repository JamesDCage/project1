name = "james"

# SQL commands to create tables
create_books = f"""
    CREATE TABLE books
        (  {name}   SERIAL PRIMARY KEY,
            isbn    VARCHAR(15),
            title   VARCHAR(63),
            author  VARCHAR(63),
            year    INT )  """

print(create_books)