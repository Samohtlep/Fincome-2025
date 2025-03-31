from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from db import DataBase
import pandas as pd
import os

class Server:
    def __init__(self, port : int = 5000):
        # Initialize the FastAPI application and the database connection

        os.makedirs("datasets", exist_ok=True)  # Ensure the 'datasets' directory exists


        self.__app = FastAPI()
        self.__app.title = "Dataset API"
        self.__app.description = "API for managing datasets"
        self.__app.version = "1.0.0"
        self.__db = DataBase()
        self.__setup_routes()

        self.__host = "localhost"
        self.__port = port

    def __setup_routes(self):
        # Define the API endpoints and their corresponding methods
        @self.__app.get("/datasets")
        async def get_datasets():
            # Retrieve all datasets from the database
            # Returns a list of datasets
            datasets = self.__db.get_datasets()
            if not datasets:
                raise HTTPException(status_code=404, detail="No datasets found")
            return datasets

        @self.__app.get("/datasets/{dataset_id}")
        async def get_dataset(dataset_id: int):
            dataset = self.__db.get_dataset_by_id(dataset_id)
            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")
            return dataset

        @self.__app.post("/datasets")
        async def import_dataset(dataset: UploadFile = File(...)):  
            file_location = f"datasets/{dataset.filename}"
            with open(file_location, "wb+") as file_object:
                file_object.write(dataset.file.read())

            # Read it with pandas
            DF = pd.read_csv(file_location)

            # Save the dataset to the database
            self.__db.insert_dataset(dataset.filename, file_location, len(DF))

            return {"filename": dataset.filename, "size": len(DF), "path": file_location}  


        @self.__app.delete("/datasets/{dataset_id}")
        async def remove_dataset(dataset_id: int):
            # Remove a dataset by its ID
            dataset = self.__db.get_dataset_by_id(dataset_id)
            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")
            self.__db.remove_dataset(dataset_id)
            return {"message": "Dataset removed successfully"}
        
    def run(self):
        # Run the FastAPI application
        uvicorn.run(self.__app, host=self.__host, port=self.__port)
    

if __name__ == "__main__":
    server = Server()
    server.run()

