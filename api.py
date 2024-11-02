from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys
from iengine_git import table_reader, truth_table, generic_truth_table, chain_reader, forward_chain, backward_chain, DPLL_reader, DPLL

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

        # Process based on method using direct imports from iengine.py
        if method == "TT":
            kb, facts, query, horn_index = table_reader(tmp_file_path)
            if horn_index == 0:
                result = truth_table(kb, facts, query)
            else:
                result = generic_truth_table(kb, facts, query)

        elif method == "FC":
            kb, facts, query = chain_reader(tmp_file_path, method)
            result = forward_chain(kb, facts, query)

        elif method == "BC":
            kb, facts, query = chain_reader(tmp_file_path, method)
            derived_facts = set()
            result = backward_chain(kb, facts, query, derived_facts)

        elif method == "DPLL":
            kb, facts, query = DPLL_reader(tmp_file_path)
            negated_query = '¬' + query if not query.startswith('¬') else query[1:]
            kb.add(negated_query)
            if DPLL(kb, facts):
                result = "NO"
            else:
                result = "> YES"

        else:
            result = "Invalid search method. Please choose among: TT, FC, BC, DPLL"

        # Clean up the temporary file
        os.unlink(tmp_file_path)

        return result

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)