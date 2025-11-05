#!/usr/bin/env python3
"""
Database table cleaning script.
Clears all data from users and all_scores tables.
"""

import sqlite3
import os
import sys
from pathlib import Path


class DatabaseCleaner:
    def __init__(self, db_name='db.sqlite'):
        self.db_path = Path(__file__).parent / db_name

    def clean_tables(self):
        """Clear all data from tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Clear users table
                cursor.execute("DELETE FROM users")
                users_deleted = cursor.rowcount

                # Clear all_scores table
                cursor.execute("DELETE FROM all_scores")
                scores_deleted = cursor.rowcount

                # Reset auto-increment counters
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='all_scores'")

                conn.commit()

                print(f"✅ Cleaned tables successfully!")
                print(f"   - Users deleted: {users_deleted}")
                print(f"   - Scores deleted: {scores_deleted}")
                print(f"   - Auto-increment counters reset")

        except sqlite3.Error as e:
            print(f"❌ Error cleaning tables: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print(f"❌ Database file not found: {self.db_path}")
            sys.exit(1)

    def verify_clean(self):
        """Verify tables are empty."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM users")
                users_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM all_scores")
                scores_count = cursor.fetchone()[0]

                if users_count == 0 and scores_count == 0:
                    print("✅ Tables are clean!")
                else:
                    print(f"⚠️  Tables still contain data: users({users_count}), scores({scores_count})")

        except sqlite3.Error as e:
            print(f"❌ Error verifying tables: {e}")


def main():
    """Main execution function."""
    print("🧹 Database Table Cleaner")
    print("-" * 25)

    cleaner = DatabaseCleaner()

    # Confirm before cleaning
    response = input("Are you sure you want to clear all table data? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)

    # Clean tables
    cleaner.clean_tables()

    # Verify cleaning
    cleaner.verify_clean()


if __name__ == "__main__":
    main()