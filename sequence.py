from typing import List, Set, Dict, Tuple, Union
from enum import Enum
import re, sys
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
        # First check if this is a TT method before validating Horn form
        is_tt = isinstance(self, TruthTable)
        
        try:
            self.kb = KnowledgeBase(clauses)
            
            # Only check Horn form requirement for chaining methods
            if not is_tt and not self.kb.is_horn_form:
                print(f"Error: Knowledge base contains non-Horn clauses. Found:")
                for clause in clauses:
                    if '||' in clause or '<=>' in clause or ('=>' in clause and '~' in clause.split('=>')[0]):
                        print(f"  - {clause}")
                print("\nOnly TT (truth table) method can be used with non-Horn clauses.")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error initializing knowledge base: {str(e)}")
            sys.exit(1)
    
    @abstractmethod
    def solve(self, query: str):
        """Solve the inference problem."""
        pass




class TruthTable(InferenceEngine):
    """Truth table checking algorithm implementation with visualization."""
    
    def _evaluate_clause(self, clause: str, model: Dict[str, bool]): # -> bool
        """Evaluate a single clause given a model."""
        # Replace symbols with their boolean values
        expr = clause
        for symbol, value in model.items():
            expr = re.sub(r'\b' + re.escape(symbol) + r'\b', str(value), expr)
        
        try:
            # Handle implications
            while '=>' in expr:
                parts = expr.split('=>', 1)
                if len(parts) != 2:
                    return False
                
                left = self._evaluate_boolean_expr(parts[0])
                right = self._evaluate_boolean_expr(parts[1])
                result = (not left) or right
                expr = str(result)
            
            return self._evaluate_boolean_expr(expr)
            
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
        """Solve using truth table method."""
        # Use get_truth_table to compute result
        truth_table = self.get_truth_table(query)
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
                    if not self._can_prove(premise, depth + 1, visited.copy()):
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
        