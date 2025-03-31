from db import DataBase

from fastapi import FastAPI, HTTPException, UploadFile, BackgroundTasks, File
from fastapi.responses import JSONResponse, FileResponse
import uvicorn

import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

class Server:
    def __init__(self, port : int = 5000):
        # Initialize the FastAPI application and the database connection
        # port : port number for the FastAPI server

        # Create the datasets directory if it doesn't exist
        os.makedirs("datasets", exist_ok=True)  

        # Initialize the FastAPI application
        self.__app = FastAPI()
        self.__app.title = "Dataset API"
        self.__app.description = "API for managing datasets"
        self.__setup_routes()

        # Initialize the database connection
        self.__db = DataBase()

        # Set the host and port for the FastAPI server
        self.__host = "localhost"
        self.__port = port

    def __setup_routes(self):
        # Define the API endpoints and their corresponding methods
        @self.__app.get("/datasets")
        async def get_datasets():
            # Retrieve all datasets from the database
            # Returns a list of datasets
            try:
                datasets = self.__db.get_datasets()
                if not datasets:
                    raise HTTPException(status_code=404, detail="No datasets found in the database.")
                return datasets
            except RuntimeError as e:
                raise HTTPException(status_code=500, detail=f"Server error: {e}")

        @self.__app.get("/datasets/{dataset_id}")
        async def get_dataset(dataset_id: int):
            # Retrieve a dataset by its ID
            # dataset_id : a valid dataset ID
            # Returns a dictionary representing the dataset
            try:
                # Check if the dataset exists
                dataset = self.__db.get_dataset_by_id(dataset_id)
                if not dataset:
                    raise HTTPException(status_code=404, detail=f"Dataset with ID {dataset_id} not found.")
                return dataset
            except RuntimeError as e:
                raise HTTPException(status_code=500, detail=f"Server error: {e}")

        @self.__app.post("/datasets")
        async def import_dataset(dataset: UploadFile = File(...)):  
            # Import a dataset from a CSV file
            # dataset : the uploaded file CSV file
            # Returns a dictionary containing the filename, size, and path of the dataset
            try:
                file_location = f"datasets/{dataset.filename}"
                with open(file_location, "wb+") as file_object:
                    file_object.write(dataset.file.read())

                # Read it with pandas
                df = pd.read_csv(file_location)

                # Save the dataset to the database
                self.__db.insert_dataset(dataset.filename, file_location, len(df))

                return {"filename": dataset.filename, "size": len(df)}  
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Bad request: {e}")
            except RuntimeError as e:
                raise HTTPException(status_code=500, detail=f"Server error: {e}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

        @self.__app.delete("/datasets/{dataset_id}")
        async def remove_dataset(dataset_id: int):
            # Remove a dataset by its ID
            # dataset_id : a valid dataset ID
            # Returns a success message if the dataset is removed successfully
            try:
                # Check if the dataset exists
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

        @self.__app.get("/datasets/{dataset_id}/excel")
        async def export_as_excel(dataset_id: int, background_tasks: BackgroundTasks):
            # Export a dataset as an Excel file
            # dataset_id : a valid dataset ID
            # Returns the Excel file as a response
            try:
                # Check if the dataset exists
                dataset = self.__db.get_dataset_by_id(dataset_id)
                if not dataset:
                    raise HTTPException(status_code=404, detail=f"Dataset with ID {dataset_id} not found.")

                # Read the dataset into a DataFrame
                df = pd.read_csv(dataset['path'])

                # Save the DataFrame to an Excel file
                excel_path = f"datasets/{dataset['filename'].replace('.csv', '.xlsx')}"
                df.to_excel(excel_path, index=False)

                # Defer the deletion of the Excel
                background_tasks.add_task(os.remove, excel_path)

                return FileResponse(excel_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=os.path.basename(excel_path))


            except HTTPException as e:
                raise e
            except RuntimeError as e:
                raise HTTPException(status_code=500, detail=f"Server error: {e}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

        @self.__app.get("/datasets/{dataset_id}/stats")
        async def get_dataset_stats(dataset_id: int):
            # Get statistics of the numerical columns in a dataset
            # dataset_id : a valid dataset ID
            # Returns a dictionary containing the statistics of the dataset
            try:
                # Check if the dataset exists
                dataset = self.__db.get_dataset_by_id(dataset_id)
                if not dataset:
                    raise HTTPException(status_code=404, detail=f"Dataset with ID {dataset_id} not found.")

                # Read the dataset into a DataFrame
                df = pd.read_csv(dataset['path'])

                # Generate stats using pandas describe()
                stats = df.describe().to_dict()

                return JSONResponse(status_code=200, content=stats)

            except HTTPException as e:
                raise e 
            except RuntimeError as e:
                raise HTTPException(status_code=500, detail=f"Server error: {e}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

        @self.__app.get("/datasets/{dataset_id}/plot")
        async def plot_dataset(dataset_id: int, background_tasks: BackgroundTasks):
            # Generate histograms for all numerical columns in a dataset and export them as a PDF
            # dataset_id : a valid dataset ID
            # Returns a PDF file containing the histograms
            try:
                # Check if the dataset exists
                dataset = self.__db.get_dataset_by_id(dataset_id)
                if not dataset:
                    raise HTTPException(status_code=404, detail=f"Dataset with ID {dataset_id} not found.")

                # Read the dataset into a DataFrame
                df = pd.read_csv(dataset['path'])

                # Generate histograms for all numerical columns
                pdf_path = f"datasets/histograms_of_{dataset['filename'].replace('.csv', '.pdf')}"
                with PdfPages(pdf_path) as pdf: # Create a PDF file to save the histograms
                    for column in df.select_dtypes(include=['float64', 'int64']).columns:
                        plt.figure(figsize=(10, 6))
                        plt.hist(df[column], bins=15, edgecolor='black')
                        plt.title(column)
                        plt.ylabel("Frequency")
                        plt.grid(True)
                        pdf.savefig()  # Save the current figure to the PDF
                        plt.close()  # Close the figure to free memory

                # Defer the deletion of the PDF
                background_tasks.add_task(os.remove, pdf_path)

                return FileResponse(pdf_path, media_type='application/pdf', filename=os.path.basename(pdf_path))

            except HTTPException as e:
                raise e 
            except RuntimeError as e:
                raise HTTPException(status_code=500, detail=f"Server error: {e}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


    def run(self):
        # Run the FastAPI application
        uvicorn.run(self.__app, host=self.__host, port=self.__port)
    

if __name__ == "__main__":
    server = Server()
    server.run()

