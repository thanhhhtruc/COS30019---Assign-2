from typing import List, Set, Dict, Tuple, Union, Optional
from enum import Enum
import re, sys, logging
from abc import ABC, abstractmethod

class LogicalConnective(Enum):
    """Enumeration of logical connectives with their symbols and descriptions.""" 
    NEGATION = ('~', 'negation')
    CONJUNCTION = ('&', 'conjunction')
    DISJUNCTION = ('||', 'disjunction')
    IMPLICATION = ('=>', 'implication')
    BICONDITIONAL = ('<=>', 'biconditional')
    
    def __init__(self, symbol: str, description: str):
        self.symbol = symbol
        self.description = description
    
    @classmethod
    def get_all_symbols(cls):   # -> Set[str]
        """Get all logical connective symbols."""
        return {member.symbol for member in cls}
    
    @classmethod
    def get_operator_pattern(cls):  # -> str
        """Get regex pattern for matching logical operators."""
        # Escape special characters and join with OR
        return '|'.join(re.escape(member.symbol) for member in cls)

class KnowledgeBase:
    """Class to manage the knowledge base and provide common utility functions."""
    
    def __init__(self, clauses: List[str]):
        """Initialize knowledge base with a list of clauses."""
        self.clauses = clauses
        self.symbols = self._extract_symbols()
        self.horn_clauses = self._parse_horn_clauses()
        self.is_horn_form = self._check_horn_form()
    
    def _extract_symbols(self):  # -> Set[str]
        """Extract all unique propositional symbols from the KB."""
        # Get pattern for all operators
        op_pattern = LogicalConnective.get_operator_pattern()
        # Split by operators and filter out empty strings
        symbols = set()
        for clause in self.clauses:
            # Replace operators with spaces
            cleaned = re.sub(op_pattern, ' ', clause)
            
            # Extract symbols (alphanumeric strings)
            symbols.update(token for token in cleaned.split() if token.isalnum() and not token.isnumeric())
        return symbols
    
    def _check_horn_form(self): # -> bool
        """Check if the knowledge base is in Horn form."""
        for clause in self.clauses:
            if '||' in clause or '<=>' in clause:
                return False
            if '=>' in clause:
                antecedent = clause.split('=>')[0]
                if '~' in antecedent:
                    return False
        return True
    
    def _parse_horn_clauses(self):
        """Parse all clauses from the knowledge base into premises and conclusions."""
        parsed_clauses = []
        
        for clause in self.clauses:
            # Skip non-Horn clauses for parsing
            if '||' in clause or '<=>' in clause:
                continue
                
            if '=>' in clause:
                try:
                    premises, conclusion = clause.split('=>')
                    premises = premises.split('&') if '&' in premises else [premises]
                    parsed_clauses.append(
                        ([premise.strip() for premise in premises], 
                        conclusion.strip())
                    )
                except ValueError:
                    print(f"Error parsing clause: {clause}")
                    continue
            else:
                # Handle simple facts
                clauses_split = [c.strip() for c in clause.split('&') if c.strip()]
                for c in clauses_split:
                    if '~' not in c:  # Skip negated facts
                        parsed_clauses.append(([], c.strip()))
                    
        return parsed_clauses

class InferenceEngine(ABC):
    """Abstract base class for inference engines."""

    def __init__(self, clauses: List[str]):
        # Check if the method is TT or DPLL, which can handle non-Horn clauses
        allows_non_horn = isinstance(self, (TruthTable, DPLL))

        try:
            self.kb = KnowledgeBase(clauses)
            
            # Only enforce Horn form requirement for chaining methods (FC, BC)
            if not allows_non_horn and not self.kb.is_horn_form:
                print(f"Error: Knowledge base contains non-Horn clauses. Only TT (Truth Table) method can be used with non-Horn clauses.")
                raise ValueError("Only TT and DPLL methods can handle non-Horn clauses.")

        except Exception as e:
            print(f"Error initializing knowledge base: {str(e)}")
            sys.exit(1)

    
    @abstractmethod
    def solve(self, query: str):
        """Solve the inference problem."""
        pass




class TruthTable(InferenceEngine):
    """Truth table checking algorithm implementation with visualization."""
    
    def _evaluate_clause(self, clause: str, model: Dict[str, bool]) -> bool:
        """Evaluate a single clause given a model."""
        # Replace symbols with their boolean values in the model
        expr = clause
        for symbol, value in model.items():
            expr = re.sub(r'\b' + re.escape(symbol) + r'\b', str(value), expr)
        
        try:
            # Convert implications manually to avoid eval issues
            expr = expr.replace('=>', ' <= ').replace('<=>', ' == ')
            expr = expr.replace('||', ' or ').replace('&', ' and ').replace('~', ' not ')
            return eval(expr)
        except Exception as e:
            print(f"Error evaluating clause '{clause}': {str(e)}")
            return False
    
    def _evaluate_boolean_expr(self, expr: str): # -> bool
        """Evaluate a boolean expression."""
        expr = expr.strip()
        expr = expr.replace('&', ' and ').replace('|', ' or ').replace('~', ' not ')
        try:
            return bool(eval(expr))
        except:
            return False

    def get_truth_table(self, query: str): # -> dict
        """Generate complete truth table data."""
        # Get sorted list of symbols
        symbols = sorted(list(self.kb.symbols))
        n_symbols = len(symbols)
        total_models = 2 ** n_symbols
        
        # Initialize truth table data
        truth_table = {
            'symbols': symbols,
            'clauses': self.kb.clauses,
            'query': query,
            'rows': []
        }
        
        # Generate all possible models
        for i in range(total_models):
            # Create model
            model = {}
            for j, symbol in enumerate(symbols):
                model[symbol] = bool((i >> j) & 1)
            
            # Evaluate clauses and query
            kb_results = []
            kb_satisfied = True
            for clause in self.kb.clauses:
                result = self._evaluate_clause(clause, model)
                kb_results.append(result)
                if not result:
                    kb_satisfied = False
            
            query_result = self._evaluate_clause(query, model)
            
            # Add row to truth table
            row = {
                'model': model,
                'kb_results': kb_results,
                'kb_satisfied': kb_satisfied,
                'query_result': query_result,
                'proves_query': kb_satisfied and query_result
            }
            truth_table['rows'].append(row)
        
        # Calculate summary
        proving_models = sum(1 for row in truth_table['rows'] 
                           if row['kb_satisfied'] and row['query_result'])
        truth_table['summary'] = {
            'total_models': total_models,
            'proving_models': proving_models,
            'is_entailed': proving_models > 0
        }
        
        return truth_table
    

    def solve(self, query: str): #  -> Tuple[bool, int]
        """Solve a propositional logic query using the truth table method.
    
        Args:
            query (str): The logical expression to evaluate against the knowledge base
            
        Returns:
            Tuple[bool, int]: A tuple containing:
                - bool: Whether the query is entailed by the knowledge base
                - int: Number of models that prove the query
        """
       # Generate complete truth table and extract results
        truth_table = self.get_truth_table(query)
        
        # Return whether query is entailed and number of proving models
        return (truth_table['summary']['is_entailed'], 
                truth_table['summary']['proving_models'])

    
class ChainingSolver(InferenceEngine):
    """Base class for chaining algorithms with common functionality."""
    
    def __init__(self, clauses: List[str]):
        super().__init__(clauses)
        self.entailed = []
        self.steps = [] # Track reasoning steps
        
    def _get_facts(self): # -> Set[str]
        """Get initial facts from the knowledge base."""
        return {conclusion for premises, conclusion in self.kb.horn_clauses if not premises}
    
    def _add_step(self, fact: str, reasoning: str, known_facts: List[str] = None):
        """Add a reasoning step with explanation."""
        step = {
            'fact': fact,
            'reasoning': reasoning,
            'known_facts': known_facts or []
        }
        self.steps.append(step)

class ForwardChaining(ChainingSolver):
    """Forward chaining algorithm implementation."""
    
    def _find_next_conclusion(self, rules, known_facts):
        """
        Find the next conclusion that can be derived, prioritizing simpler rules.
        """
        candidate_rules = []
        
        # First, gather all rules whose premises are satisfied
        for premises, conclusion in rules:
            if conclusion not in known_facts and all(p in known_facts for p in premises):
                # Calculate rule complexity (number of premises)
                complexity = len(premises)
                candidate_rules.append((complexity, premises, conclusion))
        
        if not candidate_rules:
            return None, None
            
        # Sort by complexity (fewer premises first)
        candidate_rules.sort(key=lambda x: x[0])
        _, premises, conclusion = candidate_rules[0]
        return premises, conclusion
    
    def solve(self, query: str):
        """
        Implement the forward chaining algorithm to determine if a query can be proven.
        
        Args:
            query: The query to prove
            
        Returns:
            Tuple of (whether query was proven, list of facts derived in order)
        """
        # Initialize with facts
        self.entailed = []
        self.steps = []
        
        # Initialize with facts
        facts = self._get_facts()
        for fact in sorted(facts):
            self.entailed.append(fact)
            self._add_step(
                fact=fact,
                reasoning="Initial fact from knowledge base",
                known_facts=self.entailed[:-1]
            )
            
        # Get rules (excluding pure facts)
        rules = [(premises, conclusion) 
                for premises, conclusion in self.kb.horn_clauses 
                if premises]
        
        while True:
            # Find next applicable rule based on current knowledge
            premises, conclusion = self._find_next_conclusion(rules, self.entailed)
            
            if conclusion is None:  # No more rules can be applied
                break
                
            # Apply the rule
            if conclusion not in self.entailed:
                self.entailed.append(conclusion)
                self._add_step(
                    fact=conclusion,
                    reasoning=f"Derived using: {' AND '.join(premises)}",
                    known_facts=self.entailed[:-1]
                )
            
            # Remove the used rule to prevent cyclic inference
            rules.remove((premises, conclusion))
                
        return query in self.entailed, self.entailed


class BackwardChaining(ChainingSolver):
    """Backward chaining algorithm implementation."""
    
    def _can_prove(self, query: str, visited: Set[str]): # -> bool
        """Try to prove a query using backward chaining."""
        if query in visited:
            return False
       
        visited.add(query)
        
        # Check if query is a fact
        if query in self._get_facts():
            self._add_step(
                fact=query,
                reasoning="Known fact from knowledge base",
                known_facts=self.entailed
            )
            if query not in self.entailed:
                self.entailed.append(query)
            return True
        
        
        # Try to prove through implications
        for premises, conclusion in self.kb.horn_clauses:
            if conclusion == query:
                all_premises_proven = True
                required_premises = []
                
                for premise in premises:
                    if not self._can_prove(premise, visited.copy()):
                        all_premises_proven = False
                        break
                    required_premises.append(premise)
                
                if all_premises_proven:
                    self._add_step(
                        fact=query,
                        reasoning=f"Proved using: {' AND '.join(required_premises)}",
                        known_facts=self.entailed
                    )
                    if query not in self.entailed:
                        self.entailed.append(query)
                    return True
        
        # # Try to prove through implications
        # for premises, conclusion in self.kb.horn_clauses:
        #     if conclusion == query:
        #         if all(self._can_prove(premise, visited.copy()) for premise in premises):
        #             if query not in self.entailed:
        #                 self.entailed.append(query)
        #             return True
        return False
        
        
    def solve(self, query: str): # -> Tuple[bool, List[str]]
        # self.entailed = set()
        self.entailed = []
        self.steps = []
        # Add initial goal step
        self._add_step(
            fact=query,
            reasoning="Initial goal to prove",
            known_facts=[]
        )
        result = self._can_prove(query, set())
        
        return result, self.entailed


class DPLL(InferenceEngine):
    """DPLL Algorithm class for propositional logic inference."""

    def __init__(self, clauses: List[str]):
        """Initialize the DPLL inference engine with a knowledge base."""
        super().__init__(clauses)
        self.steps = []

    def solve(self, query: str): #  -> Tuple[bool, List[str]]
        """Solve the inference problem using the DPLL algorithm."""
        self.steps.clear()
        symbols = list(self.kb.symbols)
        clauses = self._convert_clauses_to_cnf()

        # Start by setting known facts in the initial model
        initial_model = {}
        for clause in clauses:
            for literal in clause:
                if isinstance(literal, tuple):
                    symbol, is_positive = literal
                    if is_positive and symbol not in initial_model:
                        initial_model[symbol] = True

        # Perform DPLL with the initial model that includes known facts
        result = self._dpll(clauses, symbols, initial_model)
        return result, self.steps

    def _convert_clauses_to_cnf(self): #  -> List[List[Union[str, Tuple[str, bool]]]]
        """Convert KB clauses to CNF format for DPLL, including handling of <=>, =>, and ||."""
        cnf_clauses = []
        for clause in self.kb.clauses:
            # print(f"Converting clause: {clause}")  # Debug print to inspect the clause
            cnf_clauses.extend(self._convert_to_cnf(clause))
        return cnf_clauses

    def _convert_to_cnf(self, clause: str): # -> List[List[Union[str, Tuple[str, bool]]]]
        """Convert a single clause to CNF format."""
        clause = clause.replace(' ', '')
        clause = self._eliminate_biconditionals(clause)
        clause = self._eliminate_implications(clause)
        clause = self._move_negations_inwards(clause)
        return self._distribute_and_over_or(clause)

    def _eliminate_biconditionals(self, clause: str): #  -> str
        """Eliminate biconditionals (<=>) by converting them to implications."""
        while '<=>' in clause:
            left, right = clause.split('<=>', 1)
            clause = f"({left.strip()}=>{right.strip()})&({right.strip()}=>{left.strip()})"
        return clause

    def _eliminate_implications(self, clause: str): # -> str
        """Eliminate implications (=>) by converting them to disjunctions."""
        while '=>' in clause:
            left, right = clause.split('=>', 1)
            clause = f"(~{left.strip()}||{right.strip()})"
        return clause
    
    
    def _move_negations_inwards(self, clause: str): #  -> str
        """Move negations inwards using De Morgan's laws."""
        while '~(' in clause:
            start = clause.index('~(')
            end = start + 2
            open_parens = 1
            while open_parens > 0:
                if clause[end] == '(':
                    open_parens += 1
                elif clause[end] == ')':
                    open_parens -= 1
                end += 1
            sub_clause = clause[start + 2:end - 1]
            negated_sub_clause = self._negate(sub_clause)
            clause = clause[:start] + negated_sub_clause + clause[end:]
        return clause

    def _negate(self, clause: str): #  -> str
        """Negate a clause using De Morgan's laws."""
        clause = clause.replace('&&', 'TEMP')
        clause = clause.replace('||', '&&')
        clause = clause.replace('TEMP', '||')
        literals = clause.split('&&')
        negated_literals = [f"~{literal}" if not literal.startswith('~') else literal[1:] for literal in literals]
        return '||'.join(negated_literals)

    def _distribute_and_over_or(self, clause: str): # -> List[List[Union[str, Tuple[str, bool]]]]
        """Distribute AND over OR to convert to CNF."""
        if '&&' in clause:
            and_clauses = clause.split('&&')
            cnf_clauses = []
            for and_clause in and_clauses:
                cnf_clauses.extend(self._distribute_and_over_or(and_clause))
            return cnf_clauses
        elif '||' in clause:
            or_clauses = clause.split('||')
            return [[self._parse_literal(literal) for literal in or_clauses]]
        else:
            return [[self._parse_literal(clause)]]

    def _parse_literal(self, literal: str): #  -> Union[str, Tuple[str, bool]]
        """Parse a literal into a tuple of (symbol, is_positive)."""
        if literal.startswith('~'):
            return (literal[1:], False)
        else:
            return (literal, True)

    # def _dpll(self, clauses: List[List[Union[str, Tuple[str, bool]]]], symbols: List[str], model: Dict[str, bool]): #  -> bool
    #     """Recursive DPLL procedure with implications propagation."""
    #     self.steps.append(f"Current model: {model}")
        
    #     # Check if all clauses are satisfied
    #     if all(self._evaluate_clause(clause, model) for clause in clauses):
    #         self.steps.append("All clauses satisfied.")
    #         return True

    #     # Check if any clause is unsatisfiable
    #     if any(self._evaluate_clause(clause, model) is False for clause in clauses):
    #         self.steps.append("Found an unsatisfiable clause.")
    #         return False

    #     # Choose an unassigned symbol
    #     unassigned_symbols = [s for s in symbols if s not in model]
    #     if not unassigned_symbols:
    #         return False

    #     chosen_symbol = unassigned_symbols[0]

    #     # Try assigning True to the chosen symbol
    #     model[chosen_symbol] = True
    #     if self._dpll(clauses, symbols, model):
    #         return True

    #     # If assigning True didn't work, try assigning False
    #     model[chosen_symbol] = False
    #     if self._dpll(clauses, symbols, model):
    #         return True

    #     # If neither True nor False worked, backtrack
    #     del model[chosen_symbol]
    #     return False
    
    def _dpll(self, clauses, symbols, model):
        self.steps.append(f"Current model: {model}")

        # Check if all clauses are satisfied
        if all(self._evaluate_clause(clause, model) for clause in clauses):
            self.steps.append(f"Result: SAT, Model: {model.copy()}")
            return True

        # Check if any clause is unsatisfiable
        if any(self._evaluate_clause(clause, model) is False for clause in clauses):
            self.steps.append(f"Result: UNSAT, Model: {model.copy()}")
            return False

        # Choose an unassigned symbol
        unassigned_symbols = [s for s in symbols if s not in model]
        if not unassigned_symbols:
            return False

        chosen_symbol = unassigned_symbols[0]

        # Try assigning True to the chosen symbol
        model[chosen_symbol] = True
        self.steps.append(f"Exploring, Model: {model.copy()}")
        if self._dpll(clauses, symbols, model):
            return True

        # If assigning True didn't work, try assigning False
        model[chosen_symbol] = False
        self.steps.append(f"Exploring, Model: {model.copy()}")
        if self._dpll(clauses, symbols, model):
            return True

        # If neither True nor False worked, backtrack
        del model[chosen_symbol]
        self.steps.append(f"Backtrack, Model: {model}")
        return False

    def _evaluate_clause(self, clause: List[Union[str, Tuple[str, bool]]], model: Dict[str, bool]): #  -> Optional[bool]
        """Evaluate a clause under the given model."""
        result = False
        for literal in clause:
            if isinstance(literal, tuple):
                symbol, is_positive = literal
                if symbol in model:
                    if model[symbol] == is_positive:
                        return True
                    else:
                        result = result or False
                else:
                    result = None
            else:
                if literal in model:
                    if model[literal]:
                        return True
                    else:
                        result = result or False
                else:
                    result = None
        return result

    def _propagate_implications(self, clauses: List[List[Union[str, Tuple[str, bool]]]], model: Dict[str, bool]):
        """Propagate implications based on the current model."""
        # This function can be implemented to handle unit propagation and pure literal elimination
        pass