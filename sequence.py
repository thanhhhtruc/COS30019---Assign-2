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
    
    def _parse_horn_clauses(self): # -> List[Tuple[List[str], str]]
        """Parse all clauses from the knowledge base into premises and conclusions."""
        parsed_clauses = []
        for clause in self.clauses:
            if '=>' in clause:
                premises, conclusion = clause.split('=>')
                premises = premises.split('&') if '&' in premises else [premises]
                parsed_clauses.append(
                    ([premise.strip() for premise in premises], 
                    conclusion.strip())
                )
            else:
                parsed_clauses.append(([], clause.strip()))
        return parsed_clauses
    
    def normalize_expression(self, expr: str): # -> str
        """Convert expression to Python-evaluatable boolean expression."""
        expr = expr.replace(LogicalConnective.NEGATION.symbol, ' not ')
        expr = expr.replace(LogicalConnective.CONJUNCTION.symbol, ' and ')
        expr = expr.replace(LogicalConnective.DISJUNCTION.symbol, ' or ')
        # Handle implications and biconditionals specially during evaluation
        return expr


class InferenceEngine(ABC):
    """Abstract base class for inference engines."""
    
    def __init__(self, clauses: List[str]):
        self.kb = KnowledgeBase(clauses)
        
        # Only check Horn form requirement for chaining methods
        if not isinstance(self, TruthTable):
            if not self.kb.is_horn_form:
                print("Error: Knowledge base is not in Horn form. Only TT method can be used.")
                sys.exit(1)
            # raise ValueError(f"Knowledge base must be in Horn form. Only TT method can be used.") 
    
    @abstractmethod
    def solve(self, query: str): # -> Tuple[bool, Union[int, List[str]]]
        """Solve the inference problem."""
        pass


class TruthTable(InferenceEngine):
    """Truth table checking algorithm implementation."""
    
    def _evaluate_clause(self, clause: str, model: Dict[str, bool]): #  -> bool
        """Evaluate a single clause given a model."""
        # Replace symbols with their boolean values
        expr = clause
        for symbol, value in model.items():
            expr = re.sub(r'\b' + re.escape(symbol) + r'\b', str(value), expr)
        
        try:
            # Handle implications
            while '=>' in expr:
                # Find the leftmost implication
                parts = expr.split('=>', 1)
                if len(parts) != 2:
                    return False
                
                left = self._evaluate_boolean_expr(parts[0])
                right = self._evaluate_boolean_expr(parts[1])
                
                # Apply implication logic: not left or right
                result = (not left) or right
                expr = str(result)
            
            return self._evaluate_boolean_expr(expr)
            
        except Exception as e:
            print(f"Error evaluating clause '{clause}': {str(e)}")
            return False
    
    def _evaluate_boolean_expr(self, expr: str): # -> bool
        """Evaluate a boolean expression."""
        # Clean up the expression
        expr = expr.strip()
        
        # Replace operators with Python boolean operators
        expr = expr.replace('&', ' and ').replace('|', ' or ').replace('~', ' not ')
        
        try:
            return bool(eval(expr))
        except:
            return False
    
    def solve(self, query: str): #  -> Tuple[bool, int]
        """Solve using truth table method."""
        models_count = 0
        symbols = sorted(list(self.kb.symbols))
        total_models = 2 ** len(symbols)
        
        for i in range(total_models):
            # Create model
            model = {}
            for j, symbol in enumerate(symbols):
                model[symbol] = bool((i >> j) & 1)
            
            # Check if model satisfies KB and query
            kb_satisfied = all(self._evaluate_clause(clause, model) for clause in self.kb.clauses)
            if kb_satisfied and self._evaluate_clause(query, model):
                models_count += 1
        
        return models_count > 0, models_count
    
class ChainingSolver(InferenceEngine):
    """Base class for chaining algorithms with common functionality."""
    
    def __init__(self, clauses: List[str]):
        super().__init__(clauses)
        # self.entailed = set()
        self.entailed = []
        
    def _get_facts(self): # -> Set[str]
        """Get initial facts from the knowledge base."""
        return {conclusion for premises, conclusion in self.kb.horn_clauses if not premises}

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
        facts = self._get_facts()
        for fact in sorted(facts):
            self.entailed.append(fact)
            
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
        # self.entailed.add(query)
        
        # Check if query is a fact
        if query in self._get_facts():
            if query not in self.entailed:
                self.entailed.append(query)
            return True
        
        # Try to prove through implications
        for premises, conclusion in self.kb.horn_clauses:
            if conclusion == query:
                if all(self._can_prove(premise, visited.copy()) for premise in premises):
                    if query not in self.entailed:
                        self.entailed.append(query)
                    return True
        # self.entailed.remove(query)
        return False
        
        
    def solve(self, query: str): # -> Tuple[bool, List[str]]
        # self.entailed = set()
        self.entailed = []
        result = self._can_prove(query, set())
        
        return result, self.entailed
        