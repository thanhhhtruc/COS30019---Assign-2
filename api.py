from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys
from iengine import parse_input_file, get_solver

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process")
async def process_file(file: UploadFile, method: str = Form(...)):
    try:
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Parse the input file and create the solver
        kb_clauses, query = parse_input_file(tmp_file_path)
        solver = get_solver(method, kb_clauses)

        # Solve the query
        result_data = solver.solve(query)  # Expecting result_data to be a dict for DPLL
        response_data = {}

        # Format the result string
        if result_data.get("satisfiable"):
            info_str = str(result_data["satisfiable"])
            response_data["result"] = f'YES: {info_str}'
        else:
            response_data["result"] = "NO"
            
        # Include DPLL steps if the DPLL method is used
        if method == "DPLL":
            response_data["dpllSteps"] = result_data.get("dpllSteps", [])
            response_data["satisfiable"] = result_data.get("satisfiable")

        # Include truth table data if using TT method
        if method == "TT":
            truth_table = solver.get_truth_table(query)
            response_data["truthTable"] = truth_table

        # Clean up the temporary file
        os.unlink(tmp_file_path)

        return response_data

    except Exception as e:
        return {"error": str(e)}


