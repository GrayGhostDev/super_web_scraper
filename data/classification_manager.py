```python
import logging
from typing import Dict, Any, List
from datetime import datetime
from prometheus_client import Counter, Gauge
import json

logger = logging.getLogger(__name__)

# Classification metrics
classified_data = Counter(
    'classified_data_total',
    'Total classified data items',
    ['classification']
)

classification_rules = Gauge(
    'classification_rules',
    'Number of active classification rules',
    ['type']
)

class ClassificationManager:
    def __init__(self):
        self.rules = self._load_classification_rules()
        classification_rules.labels(
            type='total'
        ).set(len(self.rules))

    def classify_data(self, data: Dict[str, Any]) -> str:
        """Classify data based on defined rules."""
        try:
            classification = self._apply_rules(data)
            
            classified_data.labels(
                classification=classification
            ).inc()
            
            return classification
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            raise

    def _load_classification_rules(self) -> List[Dict[str, Any]]:
        """Load classification rules from configuration."""
        try:
            with open('config/classification_rules.json', 'r') as f:
                rules = json.load(f)
                
            return rules
            
        except Exception as e:
            logger.error(f"Error loading classification rules: {str(e)}")
            return []

    def _apply_rules(self, data: Dict[str, Any]) -> str:
        """Apply classification rules to data."""
        for rule in self.rules:
            if self._matches_rule(data, rule['conditions']):
                return rule['classification']
        
        return 'unclassified'

    def _matches_rule(
        self,
        data: Dict[str, Any],
        conditions: List[Dict[str, Any]]
    ) -> bool:
        """Check if data matches rule conditions."""
        for condition in conditions:
            field = condition['field']
            operator = condition['operator']
            value = condition['value']
            
            if not self._evaluate_condition(
                data.get(field),
                operator,
                value
            ):
                return False
        
        return True

    def _evaluate_condition(
        self,
        field_value: Any,
        operator: str,
        condition_value: Any
    ) -> bool:
        """Evaluate a single condition."""
        if operator == 'equals':
            return field_value == condition_value
        elif operator == 'contains':
            return condition_value in field_value
        elif operator == 'greater_than':
            return field_value > condition_value
        elif operator == 'less_than':
            return field_value < condition_value
        elif operator == 'exists':
            return field_value is not None
        
        return False
```