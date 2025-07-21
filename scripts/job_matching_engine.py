import json
import math
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import re

class JobMatchingEngine:
    """Advanced job matching engine with AI-powered recommendations"""
    
    def __init__(self):
        self.skill_categories = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift'],
            'web_development': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'express'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sql server'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible'],
            'data_science': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'r', 'tableau', 'power bi'],
            'mobile': ['ios', 'android', 'react native', 'flutter', 'xamarin', 'swift', 'kotlin'],
            'devops': ['jenkins', 'gitlab ci', 'github actions', 'docker', 'kubernetes', 'monitoring'],
            'design': ['figma', 'sketch', 'adobe creative suite', 'ui/ux', 'prototyping'],
            'project_management': ['agile', 'scrum', 'kanban', 'jira', 'confluence', 'project planning'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'analytical thinking']
        }
        
        self.location_weights = {
            'same_city': 1.0,
            'same_state': 0.8,
            'same_country': 0.6,
            'remote_ok': 1.0,
            'different_location': 0.3
        }
        
        self.experience_weights = {
            'exact_match': 1.0,
            'overqualified': 0.8,
            'underqualified': 0.6,
            'entry_level_exception': 0.9
        }

    def calculate_comprehensive_match(self, candidate_data: Dict, job_data: Dict) -> Dict[str, Any]:
        """Calculate comprehensive match score between candidate and job"""
        
        # Individual component scores
        skill_score = self._calculate_skill_match(candidate_data, job_data)
        experience_score = self._calculate_experience_match(candidate_data, job_data)
        location_score = self._calculate_location_match(candidate_data, job_data)
        education_score = self._calculate_education_match(candidate_data, job_data)
        preference_score = self._calculate_preference_match(candidate_data, job_data)
        
        # Weighted overall score
        weights = {
            'skills': 0.35,
            'experience': 0.25,
            'location': 0.15,
            'education': 0.15,
            'preferences': 0.10
        }
        
        overall_score = (
            skill_score * weights['skills'] +
            experience_score * weights['experience'] +
            location_score * weights['location'] +
            education_score * weights['education'] +
            preference_score * weights['preferences']
        )
        
        # Generate match insights
        match_reasons = self._generate_match_reasons(candidate_data, job_data, {
            'skill_score': skill_score,
            'experience_score': experience_score,
            'location_score': location_score,
            'education_score': education_score,
            'preference_score': preference_score
        })
        
        # AI recommendation
        ai_recommendation = self._generate_ai_recommendation(overall_score, match_reasons)
        
        return {
            'overall_score': round(overall_score, 2),
            'skill_score': round(skill_score, 2),
            'experience_score': round(experience_score, 2),
            'location_score': round(location_score, 2),
            'education_score': round(education_score, 2),
            'preference_score': round(preference_score, 2),
            'matched_skills': self._get_matched_skills(candidate_data, job_data),
            'missing_skills': self._get_missing_skills(candidate_data, job_data),
            'match_reasons': match_reasons,
            'ai_recommendation': ai_recommendation,
            'fit_analysis': self._generate_fit_analysis(candidate_data, job_data, overall_score)
        }

    def _calculate_skill_match(self, candidate_data: Dict, job_data: Dict) -> float:
        """Calculate skill matching score with category weighting"""
        candidate_skills = [skill.lower().strip() for skill in candidate_data.get('skills', [])]
        required_skills = [skill.lower().strip() for skill in job_data.get('required_skills', [])]
        preferred_skills = [skill.lower().strip() for skill in job_data.get('preferred_skills', [])]
        
        if not required_skills:
            return 75.0  # Neutral score if no requirements
        
        # Direct matches
        required_matches = len([skill for skill in required_skills if skill in candidate_skills])
        preferred_matches = len([skill for skill in preferred_skills if skill in candidate_skills])
        
        # Category-based matching (for related skills)
        category_bonus = self._calculate_category_bonus(candidate_skills, required_skills)
        
        # Calculate scores
        required_score = (required_matches / len(required_skills)) * 70
        preferred_score = (preferred_matches / len(preferred_skills)) * 20 if preferred_skills else 20
        
        total_score = required_score + preferred_score + category_bonus
        return min(100.0, total_score)

    def _calculate_category_bonus(self, candidate_skills: List[str], required_skills: List[str]) -> float:
        """Calculate bonus points for skills in same categories"""
        bonus = 0.0
        
        for required_skill in required_skills:
            if required_skill not in candidate_skills:
                # Find category of required skill
                required_category = None
                for category, skills in self.skill_categories.items():
                    if required_skill in skills:
                        required_category = category
                        break
                
                if required_category:
                    # Check if candidate has other skills in same category
                    category_skills = self.skill_categories[required_category]
                    candidate_category_skills = [skill for skill in candidate_skills if skill in category_skills]
                    
                    if candidate_category_skills:
                        bonus += min(2.0, len(candidate_category_skills) * 0.5)
        
        return min(10.0, bonus)  # Cap bonus at 10 points

    def _calculate_experience_match(self, candidate_data: Dict, job_data: Dict) -> float:
        """Calculate experience matching score"""
        candidate_exp = candidate_data.get('total_experience_years', 0)
        required_min = job_data.get('min_experience', 0)
        required_max = job_data.get('max_experience')
        
        if candidate_exp >= required_min:
            if required_max and candidate_exp > required_max:
                # Overqualified - slight penalty
                excess_years = candidate_exp - required_max
                penalty = min(20, excess_years * 2)  # 2% penalty per excess year, max 20%
                return max(60, 100 - penalty)
            else:
                # Well qualified
                return 100.0
        else:
            # Underqualified
            if required_min <= 2 and candidate_exp >= 1:
                # Entry level exception
                return 85.0
            else:
                shortage = required_min - candidate_exp
                penalty = min(40, shortage * 10)  # 10% penalty per missing year, max 40%
                return max(30, 100 - penalty)

    def _calculate_location_match(self, candidate_data: Dict, job_data: Dict) -> float:
        """Calculate location compatibility score"""
        if job_data.get('remote_ok', False):
            return 100.0
        
        candidate_location = candidate_data.get('location', '').lower()
        job_location = job_data.get('location', '').lower()
        
        if not candidate_location or not job_location:
            return 50.0  # Neutral if location not specified
        
        if candidate_location == job_location:
            return 100.0
        
        # Parse locations for city/state comparison
        candidate_parts = [part.strip() for part in candidate_location.split(',')]
        job_parts = [part.strip() for part in job_location.split(',')]
        
        if len(candidate_parts) >= 2 and len(job_parts) >= 2:
            # Same state
            if candidate_parts[-1] == job_parts[-1]:
                return 80.0
            # Same city, different state
            if candidate_parts[0] == job_parts[0]:
                return 70.0
        
        return 30.0  # Different locations

    def _calculate_education_match(self, candidate_data: Dict, job_data: Dict) -> float:
        """Calculate education matching score"""
        required_education = job_data.get('education_required', '').lower()
        
        if not required_education:
            return 75.0  # Neutral if no requirement
        
        candidate_education = candidate_data.get('education', [])
        if not candidate_education:
            return 40.0
        
        education_levels = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'mba': 4.5,
            'phd': 5,
            'doctorate': 5
        }
        
        # Find candidate's highest education level
        candidate_max_level = 0
        for edu in candidate_education:
            degree = edu.get('degree', '').lower()
            for level_name, level_value in education_levels.items():
                if level_name in degree:
                    candidate_max_level = max(candidate_max_level, level_value)
        
        # Find required education level
        required_level = 0
        for level_name, level_value in education_levels.items():
            if level_name in required_education:
                required_level = level_value
                break
        
        if candidate_max_level >= required_level:
            return 100.0
        elif candidate_max_level > 0:
            return max(50, (candidate_max_level / required_level) * 80)
        else:
            return 30.0

    def _calculate_preference_match(self, candidate_data: Dict, job_data: Dict) -> float:
        """Calculate how well job matches candidate preferences"""
        preferences = candidate_data.get('preferences', {})
        if not preferences:
            return 75.0  # Neutral if no preferences
        
        score = 0.0
        total_factors = 0
        
        # Job type preference
        preferred_types = preferences.get('job_types', [])
        if preferred_types:
            total_factors += 1
            if job_data.get('job_type') in preferred_types:
                score += 100
            else:
                score += 50
        
        # Salary preference
        min_salary = preferences.get('min_salary')
        max_salary = preferences.get('max_salary')
        job_salary_min = job_data.get('salary_min')
        job_salary_max = job_data.get('salary_max')
        
        if min_salary and job_salary_min:
            total_factors += 1
            if job_salary_min >= min_salary:
                score += 100
            else:
                score += max(30, (job_salary_min / min_salary) * 100)
        
        # Remote preference
        remote_pref = preferences.get('remote_preference')
        if remote_pref:
            total_factors += 1
            job_remote = job_data.get('remote_ok', False)
            
            if remote_pref == 'required' and job_remote:
                score += 100
            elif remote_pref == 'preferred' and job_remote:
                score += 100
            elif remote_pref == 'onsite' and not job_remote:
                score += 100
            else:
                score += 60
        
        return score / total_factors if total_factors > 0 else 75.0

    def _get_matched_skills(self, candidate_data: Dict, job_data: Dict) -> List[str]:
        """Get list of matched skills"""
        candidate_skills = [skill.lower().strip() for skill in candidate_data.get('skills', [])]
        required_skills = [skill.lower().strip() for skill in job_data.get('required_skills', [])]
        preferred_skills = [skill.lower().strip() for skill in job_data.get('preferred_skills', [])]
        
        all_job_skills = required_skills + preferred_skills
        matched = [skill for skill in all_job_skills if skill in candidate_skills]
        
        return list(set(matched))  # Remove duplicates

    def _get_missing_skills(self, candidate_data: Dict, job_data: Dict) -> List[str]:
        """Get list of missing required skills"""
        candidate_skills = [skill.lower().strip() for skill in candidate_data.get('skills', [])]
        required_skills = [skill.lower().strip() for skill in job_data.get('required_skills', [])]
        
        missing = [skill for skill in required_skills if skill not in candidate_skills]
        return missing

    def _generate_match_reasons(self, candidate_data: Dict, job_data: Dict, scores: Dict) -> List[str]:
        """Generate human-readable match reasons"""
        reasons = []
        
        if scores['skill_score'] >= 80:
            reasons.append("Strong skill alignment with job requirements")
        elif scores['skill_score'] >= 60:
            reasons.append("Good skill match with some gaps")
        
        if scores['experience_score'] >= 90:
            reasons.append("Experience level perfectly matches requirements")
        elif scores['experience_score'] >= 70:
            reasons.append("Relevant experience for the role")
        
        if scores['location_score'] >= 90:
            reasons.append("Excellent location compatibility")
        
        if scores['education_score'] >= 90:
            reasons.append("Educational background meets requirements")
        
        # Add specific skill matches
        matched_skills = self._get_matched_skills(candidate_data, job_data)
        if len(matched_skills) >= 3:
            reasons.append(f"Proficient in key technologies: {', '.join(matched_skills[:3])}")
        
        return reasons

    def _generate_ai_recommendation(self, overall_score: float, match_reasons: List[str]) -> str:
        """Generate AI-powered recommendation"""
        if overall_score >= 85:
            return "Excellent candidate match! This candidate demonstrates strong alignment across all key criteria. Highly recommended for immediate consideration."
        elif overall_score >= 70:
            return "Good candidate match with solid potential. Consider for interview to assess cultural fit and specific technical requirements."
        elif overall_score >= 55:
            return "Moderate match with some gaps. May be suitable depending on team needs and candidate's growth potential."
        else:
            return "Limited match with current requirements. Consider for future opportunities or different roles that better align with their profile."

    def _generate_fit_analysis(self, candidate_data: Dict, job_data: Dict, overall_score: float) -> Dict:
        """Generate detailed fit analysis"""
        return {
            'technical_fit': self._assess_technical_fit(candidate_data, job_data),
            'cultural_fit_indicators': self._assess_cultural_fit(candidate_data, job_data),
            'growth_potential': self._assess_growth_potential(candidate_data, job_data),
            'risk_factors': self._identify_risk_factors(candidate_data, job_data),
            'recommendations': self._generate_hiring_recommendations(overall_score)
        }

    def _assess_technical_fit(self, candidate_data: Dict, job_data: Dict) -> Dict:
        """Assess technical fit"""
        matched_skills = self._get_matched_skills(candidate_data, job_data)
        missing_skills = self._get_missing_skills(candidate_data, job_data)
        
        return {
            'strength_areas': matched_skills[:5],
            'development_areas': missing_skills[:3],
            'technical_readiness': 'High' if len(matched_skills) >= len(missing_skills) else 'Medium'
        }

    def _assess_cultural_fit(self, candidate_data: Dict, job_data: Dict) -> List[str]:
        """Assess cultural fit indicators"""
        indicators = []
        
        # Company size preference
        company_size = job_data.get('company_size', 'medium')
        if company_size == 'startup':
            indicators.append("Startup environment adaptability")
        elif company_size == 'enterprise':
            indicators.append("Enterprise-scale experience")
        
        # Remote work compatibility
        if job_data.get('remote_ok'):
            indicators.append("Remote work compatibility")
        
        return indicators

    def _assess_growth_potential(self, candidate_data: Dict, job_data: Dict) -> str:
        """Assess candidate's growth potential"""
        experience_years = candidate_data.get('total_experience_years', 0)
        education_level = len(candidate_data.get('education', []))
        
        if experience_years < 3 and education_level > 0:
            return "High - Early career with strong educational foundation"
        elif experience_years >= 3 and experience_years <= 7:
            return "Medium-High - Mid-career growth phase"
        else:
            return "Medium - Experienced professional"

    def _identify_risk_factors(self, candidate_data: Dict, job_data: Dict) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        missing_skills = self._get_missing_skills(candidate_data, job_data)
        if len(missing_skills) > 3:
            risks.append("Significant skill gaps requiring training")
        
        candidate_exp = candidate_data.get('total_experience_years', 0)
        required_min = job_data.get('min_experience', 0)
        
        if candidate_exp < required_min:
            risks.append("Below minimum experience requirement")
        
        if candidate_exp > required_min + 5:
            risks.append("Potential overqualification concerns")
        
        return risks

    def _generate_hiring_recommendations(self, overall_score: float) -> List[str]:
        """Generate specific hiring recommendations"""
        recommendations = []
        
        if overall_score >= 85:
            recommendations.extend([
                "Fast-track through interview process",
                "Consider for senior-level responsibilities",
                "Prepare competitive offer package"
            ])
        elif overall_score >= 70:
            recommendations.extend([
                "Standard interview process",
                "Assess technical skills in detail",
                "Evaluate cultural fit"
            ])
        else:
            recommendations.extend([
                "Consider for alternative roles",
                "Evaluate for future opportunities",
                "Assess training and development needs"
            ])
        
        return recommendations

    def find_best_matches_for_candidate(self, candidate_data: Dict, jobs: List[Dict], top_n: int = 10) -> List[Tuple[Dict, Dict]]:
        """Find best job matches for a candidate"""
        matches = []
        
        for job in jobs:
            if job.get('status') == 'active':
                match_data = self.calculate_comprehensive_match(candidate_data, job)
                matches.append((job, match_data))
        
        # Sort by overall score
        matches.sort(key=lambda x: x[1]['overall_score'], reverse=True)
        
        return matches[:top_n]

    def find_best_candidates_for_job(self, job_data: Dict, candidates: List[Dict], top_n: int = 20) -> List[Tuple[Dict, Dict]]:
        """Find best candidate matches for a job"""
        matches = []
        
        for candidate in candidates:
            match_data = self.calculate_comprehensive_match(candidate, job_data)
            matches.append((candidate, match_data))
        
        # Sort by overall score
        matches.sort(key=lambda x: x[1]['overall_score'], reverse=True)
        
        return matches[:top_n]

# Example usage
if __name__ == "__main__":
    engine = JobMatchingEngine()
    
    # Sample candidate
    candidate = {
        'skills': ['Python', 'Django', 'React', 'PostgreSQL', 'AWS'],
        'total_experience_years': 4,
        'location': 'San Francisco, CA',
        'education': [{'degree': 'Bachelor of Computer Science'}],
        'preferences': {
            'job_types': ['full-time'],
            'min_salary': 80000,
            'remote_preference': 'preferred'
        }
    }
    
    # Sample job
    job = {
        'title': 'Senior Python Developer',
        'required_skills': ['Python', 'Django', 'PostgreSQL'],
        'preferred_skills': ['React', 'AWS', 'Docker'],
        'min_experience': 3,
        'max_experience': 7,
        'location': 'San Francisco, CA',
        'remote_ok': True,
        'salary_min': 90000,
        'salary_max': 120000,
        'job_type': 'full-time'
    }
    
    match_result = engine.calculate_comprehensive_match(candidate, job)
    print(f"Match Score: {match_result['overall_score']}%")
    print(f"Recommendation: {match_result['ai_recommendation']}")
