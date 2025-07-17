
create table publisher(
    publisher_name varchar(100) not null,
    phone char(10) not null,
    address varchar(100) not null,
    primary key (publisher_name)
);

create table library_branch(
    branch_id integer primary key autoincrement,
    branch_name varchar(50) not null,
    branch_address varchar(100) not null
);

create table borrower(
    card_no integer PRIMARY KEY AUTOINCREMENT,
    name varchar(100) not null,
    address varchar(100) not null,
    phone char(10) not null
);

create table book(
    book_id integer primary key autoincrement,
    title varchar(100) not null,
    book_publisher varchar(100) not null,
    foreign key (book_publisher) references publisher(publisher_name)
    on delete cascade on update cascade
);

create table book_loans(
    book_id int not null,
    branch_id int not null,
    card_no int not null,
    date_out date not null,
    due_date date not null,
    Returned_date date,
    primary key (book_id, branch_id, card_no),
    foreign key (book_id) references book(book_id)
    on delete cascade on update cascade,
    foreign key (branch_id) references library_branch(branch_id)
    on delete cascade on update cascade,
    foreign key (card_no) references borrower(card_no)
    on delete cascade on update cascade
);

create table book_copies(
    book_id int not null,
    branch_id int not null,
    no_of_copies int not null,
    primary key(book_id, branch_id),
    foreign key(book_id) references book(book_id)
    on delete cascade on update cascade,
    foreign key(branch_id) references library_branch(branch_id).
    on delete cascade on update cascade
);

CREATE TRIGGER decrease_copies
    AFTER INSERT ON book_loans
    FOR EACH ROW
    BEGIN
        UPDATE book_copies
        SET no_of_copies = no_of_copies - 1
        WHERE book_id = NEW.book_id AND branch_id = NEW.branch_id;
    END;

create table book_authors(
    book_id int not null,
    author_name varchar(100) not null,
    primary key(book_id, author_name),
    foreign key(book_id) references book(book_id)
    on delete cascade on update cascade
);


--import data and csv files
.mode csv

.import --skip 1 Publisher.csv publisher 
.import --skip 1 Library_Branch.csv library_branch
.import --skip 1 Borrower.csv borrower
.import --skip 1 Book.csv book
.import --skip 1 Book_Loans.csv book_loans
.import --skip 1 Book_Copies.csv book_copies
.import --skip 1 Book_Authors.csv book_authors
