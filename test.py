import os
import sys
from time import sleep
from sequence import TruthTable, ForwardChaining, BackwardChaining, DPLL

def parse_input_file(filename):
    """Parse the input file to extract KB and query."""
    try:
        with open(filename, 'r') as file:
            content = file.readlines()
            
            # Find the indices of TELL and ASK markers
            tell_index = -1
            ask_index = -1
            for i, line in enumerate(content):
                if line.strip() == 'TELL':
                    tell_index = i
                elif line.strip() == 'ASK':
                    ask_index = i
                    
            if tell_index == -1 or ask_index == -1:
                raise ValueError("Input file must contain both TELL and ASK sections.")
                
            # Extract KB section (everything between TELL and ASK)
            kb_lines = content[tell_index + 1:ask_index]
            kb_str = ''.join(kb_lines).strip().replace(' ', '').replace('\n', '')
            
            # Extract query (everything after ASK)
            query_lines = content[ask_index + 1:]
            query = ''.join(query_lines).strip()
            
            # Split KB into clauses
            kb_clauses = [clause.strip() for clause in kb_str.split(';') if clause.strip()]
            
            return kb_clauses, query
    except FileNotFoundError:
        return None, None
    except Exception as e:
        print(f'Error parsing input file: {str(e)}')
        return None, None

def get_solver(method, kb_clauses):
    """Factory function to create appropriate solver instance."""
    solvers = {
        'TT': TruthTable,
        'FC': ForwardChaining,
        'BC': BackwardChaining,
        'DPLL': DPLL
    }
    
    solver_class = solvers.get(method)
    if not solver_class:
        raise ValueError(f"Invalid method. Please choose among: {list(solvers.keys())}")
    return solver_class(kb_clauses)

def run_inference(filename, method):
    """Run the inference engine with given filename and method."""
    try:
        # Parse input and create solver
        kb_clauses, query = parse_input_file(filename)
        if kb_clauses is None or query is None:
            return False, f"Error: Could not parse file {filename}"
            
        solver = get_solver(method, kb_clauses)
        
        # Solve and format output
        result, additional_info = solver.solve(query)
        
        if result:
            info_str = str(additional_info) if isinstance(additional_info, int) else ', '.join(additional_info)
            if method != 'DPLL':
                return True, f'YES: {info_str}'
            else:
                return True, 'YES'
        else:
            return False, "NO"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_test_files(directory):
    """Get all available test files in the directory."""
    test_files = []
    for file in os.listdir(directory):
        if file.startswith('testcase') and file.endswith('.txt'):
            try:
                num = int(file[8:-4])  # Extract number from 'testcaseX.txt'
                test_files.append((num, file))
            except ValueError:
                continue
    return sorted(test_files)  # Sort by test case number

def run_test_cases():
    """Run all test cases with different methods."""
    # Specify the directory where the script is located
    directory = os.path.dirname(os.path.abspath(__file__))
    if not directory:
        directory = '.'
    
    # List of methods for the command
    methods = ['TT', 'FC', 'BC', 'DPLL']

    # Get available test files
    test_files = get_test_files(directory)
    
    if not test_files:
        print("\nError: No test case files found!")
        print("Please ensure test files are named 'testcaseX.txt' where X is a number")
        print("and are located in the same directory as this script.")
        return

    # Print start of testing
    print("\n" + "="*50)
    print(f"Starting Test Cases Execution - Found {len(test_files)} test files")
    print("="*50 + "\n")

    # Print available test files
    print("Available test files:")
    for num, filename in test_files:
        print(f"  - {filename}")
    print("\n" + "-"*50)

    test_results = {method: {'pass': 0, 'fail': 0, 'error': 0} for method in methods}

    for num, filename in test_files:
        file_path = os.path.join(directory, filename)
        
        print(f"\nExecuting Test Case {num}")
        print("-" * 30)

        for method in methods:
            try:
                print(f"\nRunning {method} method:")
                success, result = run_inference(file_path, method)
                print(result)
                
                # Update statistics
                if 'Error' in result:
                    test_results[method]['error'] += 1
                elif success or result == 'NO':
                    test_results[method]['pass'] += 1
                else:
                    test_results[method]['fail'] += 1
                    
            except Exception as e:
                print(f"Error running {method}: {e}")
                test_results[method]['error'] += 1

            # Add a small delay between runs
            sleep(0.1)

        print("\n" + "-"*50)  # Separator between test cases

    # Print summary
    print("\nTest Summary:")
    print("="*50)
    for method in methods:
        stats = test_results[method]
        print(f"\n{method} Method:")
        print(f"  Passed: {stats['pass']}")
        print(f"  Failed: {stats['fail']}")
        print(f"  Errors: {stats['error']}")
    
    print("\n" + "="*50)
    print(f"Testing Complete! Processed {len(test_files)} test files")
    print("="*50 + "\n")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # If arguments provided, run single inference
        filename = sys.argv[1]
        method = sys.argv[2].upper()
        success, result = run_inference(filename, method)
        print(result)
    else:
        # Otherwise run all test cases
        try:
            run_test_cases()
        except KeyboardInterrupt:
            print("\nTesting interrupted by user.")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise