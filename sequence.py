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

# class DPLL(InferenceEngine):
#     """DPLL algorithm implementation with step tracking."""

#     def __init__(self, clauses: List[str]):
#         # Initialize without Horn form check
#         self.kb = KnowledgeBase(clauses)
#         self.steps = []  # Track steps for visualization

#     def solve(self, query: str) -> Dict[str, Union[bool, List[dict]]]:
#         """Solve a propositional logic query using the DPLL method."""
#         # Convert KB clauses to a list of clause sets
#         clauses = [self._parse_clause(clause) for clause in self.kb.clauses]
#         symbols = list(self.kb.symbols)
#         model = {}

#         # Perform DPLL and capture steps
#         result = self._dpll(clauses, symbols, model, self.steps)
#         return {"satisfiable": result, "dpllSteps": self.steps}

#     def _dpll(self, clauses, symbols, model, steps) -> bool:
#         """Recursive DPLL procedure with step tracking."""
#         step = {
#             'assignment': model.copy(),
#             'result': None,
#             'children': []
#         }
#         steps.append(step)  # Add current step

#         # Base cases
#         if self._all_clauses_true(clauses, model):
#             step['result'] = True
#             return True
#         if self._any_clause_false(clauses, model):
#             step['result'] = False
#             return False

#         # Choose the next symbol and copy symbols to prevent modifications
#         symbols_copy = symbols.copy()
#         symbol = symbols_copy.pop() if symbols_copy else None

#         # If no symbol is left to assign, return False (shouldn't generally reach here)
#         if not symbol:
#             step['result'] = False
#             return False

#         # Try assigning True and False with recursive tracking
#         model_true = model.copy()
#         model_true[symbol] = True
#         step_true = {'assignment': model_true, 'result': None, 'children': []}
#         step['children'].append(step_true)

#         if self._dpll(clauses, symbols_copy, model_true, step_true['children']):
#             step['result'] = True
#             return True

#         model_false = model.copy()
#         model_false[symbol] = False
#         step_false = {'assignment': model_false, 'result': None, 'children': []}
#         step['children'].append(step_false)

#         result = self._dpll(clauses, symbols_copy, model_false, step_false['children'])
#         step['result'] = result
#         return result

#     def _all_clauses_true(self, clauses, model) -> bool:
#         """Check if all clauses are true under the model."""
#         return all(self._is_clause_true(clause, model) for clause in clauses)

#     def _any_clause_false(self, clauses, model) -> bool:
#         """Check if any clause is false under the model."""
#         return any(self._is_clause_false(clause, model) for clause in clauses)

#     def _is_clause_true(self, clause, model) -> bool:
#         """Check if a clause is true under the model."""
#         for literal in clause:
#             if literal in model and model[literal] is True:
#                 return True
#             if '~' + literal in model and model['~' + literal] is False:
#                 return True
#         return False

#     def _is_clause_false(self, clause, model) -> bool:
#         """Check if a clause is false under the model."""
#         return all(
#             (literal in model and model[literal] is False) or 
#             ('~' + literal in model and model['~' + literal] is True) 
#             for literal in clause
#         )

#     def _parse_clause(self, clause: str) -> Set[str]:
#         """Parse a clause into literals."""
#         return set(clause.replace('(', '').replace(')', '').split('||'))

#     def get_steps(self):
#         """Retrieve the steps for visualization."""
#         return self.steps



# class DPLL(InferenceEngine):
#     """DPLL algorithm implementation with step tracking and improved clause handling."""
    
#     def __init__(self, clauses: List[str]):
#         super().__init__(clauses)
#         self.steps = []  # Track steps for visualization
        
#     def solve(self, query: str) -> Dict[str, Union[bool, List[dict]]]:
#         """
#         Solve a propositional logic query using the DPLL method.
#         Returns a dictionary containing only satisfiability and steps.
#         """
#         clauses = [self._parse_clause(clause) for clause in self.kb.clauses]
#         symbols = self._extract_symbols(clauses)
#         model = {}
        
#         # Add query clause to check for entailment
#         query_clause = self._parse_clause(query)
#         query_symbols = self._extract_symbols([query_clause])
#         symbols = symbols.union(query_symbols)
        
#         # Perform DPLL and capture steps
#         result = self._dpll(clauses, symbols, model)
#         return {
#             "satisfiable": result[0],
#             "dpllSteps": self.steps
#         }
    
#     def _dpll(self, clauses: List[Set[str]], symbols: Set[str], model: Dict[str, bool]) -> tuple[bool, Optional[Dict[str, bool]]]:
#         """
#         Recursive DPLL procedure with improved unit propagation and pure symbol elimination.
#         Returns (satisfiable, model) tuple.
#         """
#         # Record current step
#         step = {
#             'assignment': model.copy(),
#             'clauses': [clause.copy() for clause in clauses],
#             'symbols': symbols.copy(),
#             'children': []
#         }
#         self.steps.append(step)
        
#         # Check if all clauses are satisfied
#         if not clauses:
#             step['result'] = True
#             return True, model
        
#         # Check if any clause is empty (unsatisfiable)
#         if any(not clause for clause in clauses):
#             step['result'] = False
#             return False, None
        
#         # Unit propagation
#         unit_clause = self._find_unit_clause(clauses)
#         if unit_clause:
#             literal = next(iter(unit_clause))
#             new_model = model.copy()
#             if literal.startswith('~'):
#                 new_model[literal[1:]] = False
#             else:
#                 new_model[literal] = True
            
#             new_clauses = self._simplify_clauses(clauses, literal)
#             new_symbols = symbols - {literal.lstrip('~')}
            
#             child_step = {'type': 'unit_propagation', 'literal': literal}
#             step['children'].append(child_step)
            
#             return self._dpll(new_clauses, new_symbols, new_model)
        
#         # Pure symbol elimination
#         pure_symbol = self._find_pure_symbol(clauses, symbols)
#         if pure_symbol:
#             new_model = model.copy()
#             if pure_symbol.startswith('~'):
#                 new_model[pure_symbol[1:]] = False
#             else:
#                 new_model[pure_symbol] = True
            
#             new_clauses = self._simplify_clauses(clauses, pure_symbol)
#             new_symbols = symbols - {pure_symbol.lstrip('~')}
            
#             child_step = {'type': 'pure_symbol', 'symbol': pure_symbol}
#             step['children'].append(child_step)
            
#             return self._dpll(new_clauses, new_symbols, new_model)
        
#         # Choose a symbol for splitting
#         symbol = self._choose_symbol(symbols, clauses)
#         if not symbol:
#             step['result'] = False
#             return False, None
        
#         # Try with symbol = True
#         new_model = model.copy()
#         new_model[symbol] = True
#         new_clauses = self._simplify_clauses(clauses, symbol)
#         new_symbols = symbols - {symbol}
        
#         child_step_true = {
#             'type': 'split',
#             'symbol': symbol,
#             'value': True
#         }
#         step['children'].append(child_step_true)
        
#         result = self._dpll(new_clauses, new_symbols, new_model)
#         if result[0]:
#             step['result'] = True
#             return True, result[1]
        
#         # Try with symbol = False
#         new_model = model.copy()
#         new_model[symbol] = False
#         new_clauses = self._simplify_clauses(clauses, f"~{symbol}")
        
#         child_step_false = {
#             'type': 'split',
#             'symbol': symbol,
#             'value': False
#         }
#         step['children'].append(child_step_false)
        
#         result = self._dpll(new_clauses, new_symbols, new_model)
#         step['result'] = result[0]
#         return result
    
#     def _parse_clause(self, clause: str) -> Set[str]:
#         """Parse a clause string into a set of literals."""
#         # Remove parentheses and split by OR operator
#         literals = clause.replace('(', '').replace(')', '').split('||')
#         # Clean up each literal and handle negations
#         return {lit.strip() for lit in literals}
    
#     def _extract_symbols(self, clauses: List[Set[str]]) -> Set[str]:
#         """Extract all symbols from clauses, removing negation signs."""
#         symbols = set()
#         for clause in clauses:
#             for literal in clause:
#                 symbols.add(literal.lstrip('~'))
#         return symbols
    
#     def _find_unit_clause(self, clauses: List[Set[str]]) -> Optional[Set[str]]:
#         """Find a unit clause (clause with single literal)."""
#         for clause in clauses:
#             if len(clause) == 1:
#                 return clause
#         return None
    
#     def _find_pure_symbol(self, clauses: List[Set[str]], symbols: Set[str]) -> Optional[str]:
#         """Find a pure symbol (appears with same polarity in all clauses)."""
#         for symbol in symbols:
#             pos_count = sum(1 for clause in clauses if symbol in clause)
#             neg_count = sum(1 for clause in clauses if f"~{symbol}" in clause)
#             if pos_count > 0 and neg_count == 0:
#                 return symbol
#             if neg_count > 0 and pos_count == 0:
#                 return f"~{symbol}"
#         return None
    
#     def _choose_symbol(self, symbols: Set[str], clauses: List[Set[str]]) -> Optional[str]:
#         """Choose next symbol for splitting using a simple heuristic."""
#         if not symbols:
#             return None
#         # Choose symbol that appears most frequently
#         symbol_counts = {}
#         for symbol in symbols:
#             count = sum(1 for clause in clauses for literal in clause 
#                        if literal == symbol or literal == f"~{symbol}")
#             symbol_counts[symbol] = count
#         return max(symbol_counts.items(), key=lambda x: x[1])[0]
    
#     def _simplify_clauses(self, clauses: List[Set[str]], literal: str) -> List[Set[str]]:
#         """
#         Simplify clauses based on the assigned literal.
#         Remove clauses containing the literal and remove complement from other clauses.
#         """
#         complement = f"~{literal}" if not literal.startswith('~') else literal[1:]
#         result = []
        
#         for clause in clauses:
#             if literal in clause:
#                 continue  # Clause is satisfied
#             new_clause = clause - {complement}  # Remove complement
#             if new_clause:  # Only add non-empty clauses
#                 result.append(new_clause)
        
#         return result

#     def get_steps(self) -> List[dict]:
#         """Return the solution steps for visualization."""
#         return self.steps




# Correct DPLL

class DPLL(InferenceEngine):
    """DPLL algorithm implementation with step tracking."""
    
    def __init__(self, clauses: List[str]):
        super().__init__(clauses)
        self.steps = []  # Track steps for visualization
        self.model = {}  # Track the final model
        
    def solve(self, query: str): #  -> Tuple[bool, List[str]]
        """
        Solve a propositional logic query using the DPLL method.
        Returns (satisfiable, assignment_steps) where assignment_steps shows how variables were assigned.
        """
        clauses = [self._parse_clause(clause) for clause in self.kb.clauses]
        symbols = self._extract_symbols(clauses)
        self.model = {}
        self.steps = []  # Reset steps for new solving attempt
        
        # Add query clause to check for entailment
        query_clause = self._parse_clause(query)
        query_symbols = self._extract_symbols([query_clause])
        symbols = symbols.union(query_symbols)
        
        # Perform DPLL
        result = self._dpll(clauses, symbols, self.model)
        logging.info(f"DPLL result: {result[0]}; Steps recorded: {self.steps}")
        return result[0], self.steps
    
    def _dpll(self, clauses: List[Set[str]], symbols: Set[str], model: Dict[str, bool]): #  -> tuple[bool, Optional[Dict[str, bool]]]
        """
        Recursive DPLL procedure with unit propagation and pure symbol elimination.
        """
        # Check if all clauses are satisfied
        if not clauses:
            self.model.update(model)
            return True, model
        
        # Check if any clause is empty (unsatisfiable)
        if any(not clause for clause in clauses):
            return False, None
        
        # Unit propagation
        unit_clause = self._find_unit_clause(clauses)
        if unit_clause:
            literal = next(iter(unit_clause))
            new_model = model.copy()
            is_positive = not literal.startswith('~')
            symbol = literal[1:] if not is_positive else literal
            new_model[symbol] = is_positive
            
            # Record unit propagation step
            self.steps.append(f"\n\tUnit propagation: {symbol}={'T' if is_positive else 'F'}")
            
            new_clauses = self._simplify_clauses(clauses, literal)
            new_symbols = symbols - {symbol}
            
            return self._dpll(new_clauses, new_symbols, new_model)
        
        # Pure symbol elimination
        pure_symbol = self._find_pure_symbol(clauses, symbols)
        if pure_symbol:
            new_model = model.copy()
            is_positive = not pure_symbol.startswith('~')
            symbol = pure_symbol[1:] if not is_positive else pure_symbol
            new_model[symbol] = is_positive
            
            # Record pure symbol elimination step
            self.steps.append(f"\n\tPure symbol elimination: {symbol}={'T' if is_positive else 'F'}")
            
            new_clauses = self._simplify_clauses(clauses, pure_symbol)
            new_symbols = symbols - {symbol}
            
            return self._dpll(new_clauses, new_symbols, new_model)
        
        # Choose a symbol for splitting
        symbol = self._choose_symbol(symbols, clauses)
        if not symbol:
            return False, None
        
        # Try with symbol = True
        new_model = model.copy()
        new_model[symbol] = True
        self.steps.append(f"Splitting: trying {symbol}=T")
        new_clauses = self._simplify_clauses(clauses, symbol)
        new_symbols = symbols - {symbol}
        
        result = self._dpll(new_clauses, new_symbols, new_model)
        if result[0]:
            return True, result[1]
        
        # Try with symbol = False
        new_model = model.copy()
        new_model[symbol] = False
        self.steps.append(f"Splitting: trying {symbol}=F")
        new_clauses = self._simplify_clauses(clauses, f"~{symbol}")
        
        return self._dpll(new_clauses, new_symbols, new_model)

    def _parse_clause(self, clause: str): #  -> Set[str]
        """Parse a clause string into a set of literals."""
        literals = clause.replace('(', '').replace(')', '').split('||')
        return {lit.strip() for lit in literals}
    
    def _extract_symbols(self, clauses: List[Set[str]]): #  -> Set[str]
        """Extract all symbols from clauses, removing negation signs."""
        symbols = set()
        for clause in clauses:
            for literal in clause:
                symbols.add(literal.lstrip('~'))
        return symbols
    
    def _find_unit_clause(self, clauses: List[Set[str]]): #  -> Optional[Set[str]]
        """Find a unit clause (clause with single literal)."""
        for clause in clauses:
            if len(clause) == 1:
                return clause
        return None
    
    def _find_pure_symbol(self, clauses: List[Set[str]], symbols: Set[str]): #  -> Optional[str]
        """Find a pure symbol (appears with same polarity in all clauses)."""
        for symbol in symbols:
            pos_count = sum(1 for clause in clauses if symbol in clause)
            neg_count = sum(1 for clause in clauses if f"~{symbol}" in clause)
            if pos_count > 0 and neg_count == 0:
                return symbol
            if neg_count > 0 and pos_count == 0:
                return f"~{symbol}"
        return None
    
    def _choose_symbol(self, symbols: Set[str], clauses: List[Set[str]]): # -> Optional[str]
        """Choose next symbol for splitting using a simple heuristic."""
        if not symbols:
            return None
        return next(iter(symbols))  # Simple selection of first symbol
    
    def _simplify_clauses(self, clauses: List[Set[str]], literal: str): #  -> List[Set[str]]
        """Simplify clauses based on the assigned literal."""
        complement = f"~{literal}" if not literal.startswith('~') else literal[1:]
        result = []
        
        for clause in clauses:
            if literal in clause:
                continue  # Clause is satisfied
            new_clause = clause - {complement}  # Remove complement
            if new_clause:  # Only add non-empty clauses
                result.append(new_clause)
        
        return result




