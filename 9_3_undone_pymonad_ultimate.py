import csv

from pymonad.either import Left, Right
from pymonad.io import IO
from pymonad.tools import curry


# Function to handle file reading
def read_csv_file(file_path):
    try:
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            data = [row for row in reader]
        return Right(data)
    except FileNotFoundError:
        return Left("Error: File not found")


def remove_header(data):
    try:
        return Right(data[1:])
    except IndexError:
        return Left("Error: Unable to remove header")


@curry(2)
def extract_column(column_index, data):
    return Right(data).bind(
        lambda rows: Right(list(map(lambda row: row[column_index], rows)))
    )


extract_score_column = extract_column(1)
extract_name_column = extract_column(0)


def convert_to_float(data):
    try:
        return Right(list(map(float, data)))
    except ValueError:
        return Left("Error: Unable to convert to float")


def calculate_average(column_values):
    try:
        return Right(sum(column_values) / len(column_values))
    except ZeroDivisionError:
        return Left("Error: Division by zero")


csv_file_path = "example.csv"
names = IO(
    read_csv_file(csv_file_path).then(remove_header).then(extract_name_column)
).value


result = IO(
    read_csv_file(csv_file_path)
    .then(remove_header)
    .then(extract_score_column)
    .then(convert_to_float)
    .then(calculate_average)
).value


def handle_error(error):
    print(f"Error processing data: {error}")


def handle_success(names, result):
    print(f"An average score of {', '.join(names[:-1])} and {names[-1]} is {result}")


names.either(
    handle_error,
    lambda names: result.either(
        lambda error: handle_error(error), lambda result: handle_success(names, result)
    ),
)
