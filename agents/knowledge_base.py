"""
LLM-only Knowledge Base stubs (no CSV).
Agents should rely on LLM prompts; this module provides empty fallbacks.
"""

from typing import Dict, List, Any, Optional, Tuple
import json
from pathlib import Path

class KnowledgeBaseManager:
    """LLM-only knowledge base interface (no CSV)."""
    def __init__(self, data_dir: str = "."):
        self.data_dir = Path(data_dir)
        self._fertilizer_db = None
        self._crop_db = None
        self._irrigation_db = None
        self._regional_db = None
    
    # =============================================================================
    # FERTILIZER KNOWLEDGE METHODS
    # =============================================================================
    
    def get_fertilizer_recommendations(self, criteria: Optional[Dict[str, Any]] = None) -> List[Dict]:
        return []
    
    def get_fertilizer_by_type(self, fertilizer_types: List[str]) -> List[Dict]:
        return []
    
    def get_fertilizer_combinations(self, primary_fert: str, secondary_fert: Optional[str] = None) -> Dict:
        return {}
    
    def get_nutrient_analysis(self, fertilizers: List[str]) -> Dict:
        return {}
    
    # =============================================================================
    # CROP VARIETY METHODS
    # =============================================================================
    
    def get_varieties_for_region(self, region: str, altitude: Optional[int] = None) -> List[Dict]:
        return []
    
    def get_variety_comparison(self, varieties: List[str]) -> List[Dict]:
        return []
    
    def get_varieties_by_maturity(self, maturity_group: Optional[str] = None, max_days: Optional[int] = None) -> List[Dict]:
        return []
    
    # =============================================================================
    # IRRIGATION METHODS
    # =============================================================================
    
    def get_irrigation_recommendations(self, criteria: Optional[Dict[str, Any]] = None) -> List[Dict]:
        return []
    
    def get_irrigation_efficiency_analysis(self, methods: List[str]) -> Dict:
        return {}
    
    # =============================================================================
    # REGIONAL & ENVIRONMENTAL METHODS
    # =============================================================================
    
    def get_regional_info(self, region: str = "Trans Nzoia") -> Dict:
        return {
            "region": region,
            "rainfall": "1200-1400 mm/year",
            "altitude": "1800-2200 m",
            "soil": "Deep volcanic soils"
        }
    
    def get_similar_regions(self, target_region: str) -> List[Dict]:
        return []
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def _in_range(self, value: float, range_str: str) -> bool:
        """Check if value is in range string like '4-8'"""
        try:
            if '-' in str(range_str):
                min_val, max_val = map(float, str(range_str).split('-'))
                return min_val <= value <= max_val
            return True
        except:
            return True
    
    def _calculate_variety_suitability(self, variety: Dict[str, Any], region: str, altitude: Optional[int]) -> float:
        """Stub scoring (LLM-only flow); not used when CSV disabled."""
        return 0.0
    
    def _calculate_regional_similarity(self, region1: Dict, region2: Dict) -> float:
        """Calculate similarity score between regions"""
        score = 0
        
        # Altitude similarity
        alt_diff = abs(region1['altitude_max'] - region2['altitude_max'])
        score += max(0, 20 - alt_diff/50)  # Max 20 points
        
        # Rainfall similarity
        rain_diff = abs(region1['rainfall_annual'] - region2['rainfall_annual'])
        score += max(0, 30 - rain_diff/50)  # Max 30 points
        
        # Temperature similarity
        temp_diff = abs(region1['temp_avg_max'] - region2['temp_avg_max'])
        score += max(0, 20 - temp_diff/2)  # Max 20 points
        
        # Soil type similarity
        if region1['soil_type_primary'] == region2['soil_type_primary']:
            score += 30
        
        return score
        # Simple stub similarity
        score += 0
    
    def get_experiment_context(self, experiment_type: str, region: str = "Trans Nzoia") -> Dict:
        """Get comprehensive context for experiment design"""
        context = {
            'regional_info': self.get_regional_info(region),
            'experiment_type': experiment_type,
            'recommendations': {}
        }
        
        if experiment_type == 'fertilizer':
            context['recommendations']['fertilizers'] = self.get_fertilizer_recommendations()
            context['recommendations']['popular_combinations'] = self._get_popular_fertilizer_combinations()
        
        elif experiment_type == 'irrigation':
            context['recommendations']['irrigation'] = self.get_irrigation_recommendations({'smallholder': True})
        
        elif experiment_type == 'variety':
            region_info = context['regional_info']
            altitude = region_info.get('altitude_max', 2000) if region_info else 2000
            context['recommendations']['varieties'] = self.get_varieties_for_region(region, altitude)
        
        return context
    
    def _get_popular_fertilizer_combinations(self) -> List[Dict]:
        """Get popular fertilizer combinations from the database"""
        if self._fertilizer_db is None:
            return []
        
        combinations = []
        
        # Get fertilizers with combination examples
        combo_ferts = self._fertilizer_db[
            self._fertilizer_db['combined_use_examples'].notna() & 
            (self._fertilizer_db['combined_use_examples'] != 'N/A')
        ]
        
        for _, fert in combo_ferts.iterrows():
            combinations.append({
                'primary': fert['product_name'],
                'example': fert['combined_use_examples'],
                'efficiency': fert['efficiency_rating']
            })
        
        return combinations[:10]  # Top 10 combinations

# Global instance for easy access
knowledge_base = KnowledgeBaseManager()
