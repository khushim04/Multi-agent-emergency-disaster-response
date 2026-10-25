
import sqlite3
from pathlib import Path


# Store the database in the project directory.
DB_PATH = Path(__file__).resolve().parent / "shelters.db"


def get_connection():
    """Create a connection to the shelter database."""

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    """Create the shelters table if it does not exist."""

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS shelters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                address TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity >= 0),
                available_places INTEGER NOT NULL
                    CHECK (available_places >= 0),
                contact_number TEXT,
                verified INTEGER NOT NULL DEFAULT 0
                    CHECK (verified IN (0, 1)),
                CHECK (available_places <= capacity)
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_shelters_city
            ON shelters(city)
            """
        )

    print("Shelter database and table are ready.")


def add_shelter(
    name: str,
    city: str,
    address: str,
    capacity: int,
    available_places: int,
    contact_number: str = "",
    verified: bool = False,
):
    """Insert a shelter record into the database."""

    if not name.strip() or not city.strip() or not address.strip():
        raise ValueError("Name, city, and address are required.")

    if capacity < 0 or available_places < 0:
        raise ValueError("Capacity cannot be negative.")

    if available_places > capacity:
        raise ValueError(
            "Available places cannot exceed total capacity."
        )

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO shelters (
                name,
                city,
                address,
                capacity,
                available_places,
                contact_number,
                verified
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name.strip(),
                city.strip(),
                address.strip(),
                capacity,
                available_places,
                contact_number.strip(),
                int(verified),
            ),
        )

    print(f"Shelter record added: {name}")


def find_shelters(city: str, minimum_places: int = 1) -> list[dict]:
    """Find shelters in a city with sufficient available capacity."""

    if not city.strip():
        raise ValueError("Please provide a city name.")

    if minimum_places < 0:
        raise ValueError("Minimum places cannot be negative.")

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                name,
                city,
                address,
                capacity,
                available_places,
                contact_number,
                verified
            FROM shelters
            WHERE city = ? COLLATE NOCASE
              AND available_places >= ?
              AND verified = 1
            ORDER BY available_places DESC
            """,
            (city.strip(), minimum_places),
        ).fetchall()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    create_table()

    print(f"Database location: {DB_PATH}")
    print("Shelter database setup completed.")
