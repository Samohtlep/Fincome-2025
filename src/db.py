import sqlite3
class DataBase:
    def __init__(self):
        # Initialize the database connection and create the datasets table if it doesn't exist
        self.__conn = sqlite3.connect('data.db')
        self.__conn.row_factory = sqlite3.Row
        self.__conn.execute('''CREATE TABLE IF NOT EXISTS datasets (
                            'id' INTEGER PRIMARY KEY AUTOINCREMENT, 
                            'filename' TEXT NOT NULL, 
                            'path' TEXT NOT NULL,
                            'size' INTEGER NOT NULL
                            )''')
        self.__conn.commit()

    def insert_dataset(self, filename : str, path : str, size : int):
        # Insert a new dataset into the datasets table
        # filename : name of the dataset file
        # path : path to the dataset file
        # size : size of the dataset file in bytes
        self.__conn.execute('''INSERT INTO datasets (filename, path, size) 
                            VALUES (?, ?, ?)''', (filename, path, size))
        self.__conn.commit()

    def get_datasets(self) -> list[dict] :
        # Retrieve all datasets from the datasets table
        # Returns a list of dictionaries, each representing a dataset
        cursor = self.__conn.execute('''SELECT * FROM datasets''')
        datasets = cursor.fetchall()
        return datasets
    
    def get_dataset_by_id(self, dataset_id : int) -> dict :
        # Retrieve a dataset by its 
        # dataset_id : a valid dataset ID
        # Returns a dictionary representing the dataset
        cursor = self.__conn.execute('''SELECT * FROM datasets WHERE id = ?''', (dataset_id,))
        dataset = cursor.fetchone()
        return dataset
    
    def remove_dataset(self, dataset_id : int):
        # Remove a dataset by its ID
        self.__conn.execute('''DELETE FROM datasets WHERE id = ?''', (dataset_id,))
        self.__conn.commit()


    def __del__(self):
        # Close the database connection when the object is deleted
        self.__conn.close()

if __name__ == '__main__':
    db = DataBase()
    db.insert_dataset('example.csv', '/path/to/example.csv', 1024)
    datasets = db.get_datasets()
    for dataset in datasets:
        print(dataset['filename'], dataset['path'], dataset['size'])
    db.remove_dataset(1)
