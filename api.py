from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os, logging
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

        # Initialize response data
        response_data = {}

        if method == "DPLL":
            # Solve the query using DPLL, expecting a dictionary with `satisfiable` and `dpllSteps`
            
            # result_data = solver.solve(query)  # DPLL should return a dict
            # response_data["result"] = "YES" if result_data.get("satisfiable") else "NO"
            # response_data["dpllSteps"] = result_data.get("dpllSteps", [])
            # response_data["satisfiable"] = result_data.get("satisfiable")
            
            # satisfiable, assignment_steps = solver.solve(query)
            # response_data["result"] = "YES" if satisfiable else "NO"
            # response_data["dpllSteps"] = assignment_steps
            # response_data["satisfiable"] = satisfiable
            # logging.info(f"Response data for DPLL: {response_data}")
            
            # Get the result from DPLL solver
            satisfiable, steps = solver.solve(query)
            
            # Process the steps into the expected format
            formatted_steps = []
            for i, step in enumerate(steps):
                # Your solver returns steps as strings, so we need to parse them
                step_info = {
                    "stepNumber": i + 1,
                    "assignment": step,  # The full step string
                    "result": "Success" if "trying" not in step.lower() else "Trying",
                    "action": "Unit Propagation" if "unit propagation" in step.lower() else
                             "Pure Symbol" if "pure symbol" in step.lower() else
                             "Split" if "splitting" in step.lower() else "Assignment"
                }
                formatted_steps.append(step_info)

            response_data = {
                "result": "YES" if satisfiable else "NO",
                "satisfiable": satisfiable,
                "dpllSteps": formatted_steps
            }
            logging.info(f"DPLL Steps generated: {len(response_data['dpllSteps'])} steps")
        
        
        else:
            # Solve the query for other methods, expecting a tuple of (result, additional_info)
            result, additional_info = solver.solve(query)

            # Format the result string
            if result:
                info_str = str(additional_info) if isinstance(additional_info, int) else ', '.join(additional_info)
                response_data["result"] = f'YES: {info_str}'
            else:
                response_data["result"] = "NO"

            # Include truth table data if using TT method
            if method == "TT":
                truth_table = solver.get_truth_table(query)
                response_data["truthTable"] = truth_table

        # Clean up the temporary file
        os.unlink(tmp_file_path)

        return response_data

    except Exception as e:
        return {"error": str(e)}
