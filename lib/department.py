#lib/department.py
from __init__ import CURSOR, CONN


class Department:
    # Class attribute to store all instantiated Department objects by their database ID
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Department instances """
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT)
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Department instances """
        sql = """
            DROP TABLE IF EXISTS departments;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the name and location values of the current Department instance.
        Update object id attribute using the primary key value of new row and save to the 'all' dictionary.
        """
        sql = """
            INSERT INTO departments (name, location)
            VALUES (?, ?)
        """

        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()

        self.id = CURSOR.lastrowid
        # Add the instance to the class dictionary
        type(self).all[self.id] = self

    @classmethod
    def create(cls, name, location):
        """ Initialize a new Department instance and save the object to the database """
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        """Update the table row corresponding to the current Department instance."""
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Department instance and remove it from the 'all' dictionary.
        Set the instance's id to None.
        """
        sql = """
            DELETE FROM departments
            WHERE id = ?
        """

        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        # Remove from the 'all' dictionary and set the instance id to None
        del type(self).all[self.id]
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        """Given a row from the database, return the corresponding Department instance.
        If the instance already exists in the 'all' dictionary, return that one; otherwise, create a new instance.
        """
        # Check the 'all' dictionary first
        department = cls.all.get(row[0])
        if department:
            # Update existing instance's attributes in case they changed
            department.name = row[1]
            department.location = row[2]
        else:
            # Create a new instance
            department = cls(row[1], row[2], row[0])
            # Add the new instance to the 'all' dictionary
            cls.all[department.id] = department
        return department

    @classmethod
    def get_all(cls):
        """Return a list of Department instances for every row in the db."""
        sql = """
            SELECT *
            FROM departments
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        """Return a Department instance corresponding to the db row retrieved by id."""
        sql = """
            SELECT *
            FROM departments
            WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Return a Department instance corresponding to the db row retrieved by name."""
        sql = """
            SELECT *
            FROM departments
            WHERE name = ?
        """
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None