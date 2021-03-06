import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    file = open("books.csv")
    reader = csv.reader(file)
    reader.__next__()
    for isbn, title, author, year in reader:

        db.execute("INSERT INTO Book(Isbn, Title, Author, Year) VALUES (:isbn,:title,:author,:year)",
        {"isbn": isbn, "title": title, "author": author, "year": year})

        print(f"Added isbn:{isbn}, title:{title}, author:{author}, year:{year}")
        
    db.commit()

if __name__ == "__main__":
    main()