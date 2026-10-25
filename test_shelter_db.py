
from shelter_db import (
    create_table,
    add_shelter,
    find_shelters,
)


def main():
    create_table()

    # These are fictional records for testing only.
    # They are NOT real or verified emergency shelters.
    test_shelters = [
        {
            "name": "TEST Shelter A",
            "city": "Bhopal",
            "address": "TEST ADDRESS A",
            "capacity": 100,
            "available_places": 40,
            "contact_number": "TEST CONTACT A",
        },
        {
            "name": "TEST Shelter B",
            "city": "Bhopal",
            "address": "TEST ADDRESS B",
            "capacity": 50,
            "available_places": 10,
            "contact_number": "TEST CONTACT B",
        },
        {
            "name": "TEST Shelter C",
            "city": "Indore",
            "address": "TEST ADDRESS C",
            "capacity": 80,
            "available_places": 30,
            "contact_number": "TEST CONTACT C",
        },
    ]

    # Add each test record only if it does not already exist.
    from shelter_db import get_connection

    with get_connection() as connection:
        for shelter in test_shelters:
            exists = connection.execute(
                """
                SELECT id FROM shelters
                WHERE name = ? AND city = ?
                """,
                (shelter["name"], shelter["city"]),
            ).fetchone()

            
            if exists is None:
                add_shelter(**shelter, verified=False)
            else:
                connection.execute(
                    """
                    UPDATE shelters
                    SET verified = 0
                    WHERE name = ? AND city = ?
                    """,
                    (shelter["name"], shelter["city"]),
                )
                

    print("\n--- Bhopal lookup: minimum 20 places ---")
    results = find_shelters("Bhopal", minimum_places=20)

    # Test records are unverified, so they must not be returned.
    assert results == [], (
        "Unverified shelters must not appear in search results."
    )

    print("PASS: Unverified test shelters were excluded.")

    print("\n--- Mark one test record verified for query testing ---")
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE shelters
            SET verified = 1
            WHERE name = ? AND city = ?
            """,
            ("TEST Shelter A", "Bhopal"),
        )

    results = find_shelters("Bhopal", minimum_places=20)

    for shelter in results:
        print(
            f"{shelter['name']} | "
            f"Available: {shelter['available_places']} | "
            f"Address: {shelter['address']}"
        )

    assert len(results) == 1, (
        "Expected only TEST Shelter A in the search results."
    )
    assert results[0]["name"] == "TEST Shelter A"

    print("\nPASS: City, capacity, and verification filters work.")
    print("All shelter database tests passed.")


if __name__ == "__main__":
    main()
