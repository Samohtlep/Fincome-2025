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
            try:
                # Retrieve all datasets from the database
                # Returns a list of datasets
                datasets = self.__db.get_datasets()
                if not datasets:
                    raise HTTPException(status_code=404, detail="No datasets found in the database.")
                return datasets
            except RuntimeError as e:
                raise HTTPException(status_code=500, detail=f"Server error: {e}")

        @self.__app.get("/datasets/{dataset_id}")
        async def get_dataset(dataset_id: int):
            try:
                dataset = self.__db.get_dataset_by_id(dataset_id)
                if not dataset:
                    raise HTTPException(status_code=404, detail=f"Dataset with ID {dataset_id} not found.")
                return dataset
            except RuntimeError as e:
                raise HTTPException(status_code=500, detail=f"Server error: {e}")

        @self.__app.post("/datasets")
        async def import_dataset(dataset: UploadFile = File(...)):  
            try:
                file_location = f"datasets/{dataset.filename}"
                with open(file_location, "wb+") as file_object:
                    file_object.write(dataset.file.read())

                # Read it with pandas
                DF = pd.read_csv(file_location)

                # Save the dataset to the database
                self.__db.insert_dataset(dataset.filename, file_location, len(DF))

                return {"filename": dataset.filename, "size": len(DF), "path": file_location}  
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Bad request: {e}")
            except RuntimeError as e:
                raise HTTPException(status_code=500, detail=f"Server error: {e}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

        @self.__app.delete("/datasets/{dataset_id}")
        async def remove_dataset(dataset_id: int):
            try:
                dataset = self.__db.get_dataset_by_id(dataset_id)
                if not dataset:
                    raise HTTPException(status_code=404, detail=f"Dataset with ID {dataset_id} not found.")

                # Remove the dataset from the database
                self.__db.remove_dataset(dataset_id)

                # Delete the file from the filesystem
                if os.path.exists(dataset['path']):
                    os.remove(dataset['path'])

                return JSONResponse(status_code=200, content={"message": "Dataset removed successfully."})

            except HTTPException as e:
                # If an HTTPException (like 404) was already raised, just re-raise it
                raise e
            except RuntimeError as e:
                raise HTTPException(status_code=500, detail=f"Server error: {e}")
            except Exception as e:
                # Catch all other unexpected exceptions and return a proper 500 error
                raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    def run(self):
        # Run the FastAPI application
        uvicorn.run(self.__app, host=self.__host, port=self.__port)
    

if __name__ == "__main__":
    server = Server()
    server.run()

