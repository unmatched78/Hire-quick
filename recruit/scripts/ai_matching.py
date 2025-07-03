import json
import math
from typing import Dict, List, Any, Tuple

def calculate_experience_score(candidate_exp: List[Dict], job_requirements: Dict) -> float:
    """Calculate experience match score based on years and relevance"""
    required_years = job_requirements.get('min_experience', 0)
    
    # Calculate total years of experience
    total_years = 0
    for exp in candidate_exp:
        # Simple year calculation (can be improved with date parsing)
        if 'start_date' in exp and 'end_date' in exp:
            try:
                start_year = int(exp['start_date'][-4:]) if exp['start_date'][-4:].isdigit() else 2020
                end_year = int(exp['end_date'][-4:]) if exp['end_date'][-4:].isdigit() else 2024
                total_years += max(0, end_year - start_year)
            except:
                total_years += 1  # Default to 1 year if parsing fails
    
    # Score based on experience requirements
    if total_years >= required_years:
        return min(100, (total_years / max(required_years, 1)) * 50 + 50)
    else:
        return (total_years / max(required_years, 1)) * 50

def calculate_education_score(candidate_edu: List[Dict], job_requirements: Dict) -> float:
    """Calculate education match score"""
    required_degree = job_requirements.get('required_degree', '').lower()
    
    if not required_degree:
        return 50  # Neutral score if no requirement
    
    degree_hierarchy = {
        'high school': 1,
        'associate': 2,
        'bachelor': 3,
        'master': 4,
        'phd': 5,
        'doctorate': 5
    }
    
    candidate_max_level = 0
    for edu in candidate_edu:
        degree = edu.get('degree', '').lower()
        for level_name, level_value in degree_hierarchy.items():
            if level_name in degree:
                candidate_max_level = max(candidate_max_level, level_value)
    
    required_level = 0
    for level_name, level_value in degree_hierarchy.items():
        if level_name in required_degree:
            required_level = level_value
            break
    
    if candidate_max_level >= required_level:
        return 100
    elif candidate_max_level > 0:
        return (candidate_max_level / max(required_level, 1)) * 70
    else:
        return 20  # Some credit for unspecified education

def calculate_location_score(candidate_location: str, job_location: str, remote_ok: bool = False) -> float:
    """Calculate location compatibility score"""
    if remote_ok or job_location.lower() == 'remote':
        return 100
    
    if not candidate_location or not job_location:
        return 50  # Neutral if location not specified
    
    candidate_location = candidate_location.lower()
    job_location = job_location.lower()
    
    if candidate_location == job_location:
        return 100
    
    # Check for same city/state
    candidate_parts = candidate_location.split(',')
    job_parts = job_location.split(',')
    
    if len(candidate_parts) >= 2 and len(job_parts) >= 2:
        # Same state
        if candidate_parts[-1].strip() == job_parts[-1].strip():
            return 70
        # Same city
        if candidate_parts[0].strip() == job_parts[0].strip():
            return 80
    
    return 30  # Different locations, not remote

def calculate_overall_match_score(candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, float]:
    """Calculate comprehensive match score between candidate and job"""
    
    # Extract job requirements
    job_requirements = {
        'required_skills': job.get('required_skills', []),
        'preferred_skills': job.get('preferred_skills', []),
        'min_experience': job.get('min_experience', 0),
        'required_degree': job.get('required_degree', ''),
        'location': job.get('location', ''),
        'remote_ok': job.get('remote_ok', False)
    }
    
    # Calculate individual scores
    skill_score = calculate_skill_match_advanced(
        candidate.get('skills', []), 
        job_requirements['required_skills'],
        job_requirements['preferred_skills']
    )
    
    experience_score = calculate_experience_score(
        candidate.get('experience', []), 
        job_requirements
    )
    
    education_score = calculate_education_score(
        candidate.get('education', []), 
        job_requirements
    )
    
    location_score = calculate_location_score(
        candidate.get('contact_info', {}).get('location', ''),
        job_requirements['location'],
        job_requirements['remote_ok']
    )
    
    # Weighted overall score
    weights = {
        'skills': 0.4,
        'experience': 0.3,
        'education': 0.2,
        'location': 0.1
    }
    
    overall_score = (
        skill_score * weights['skills'] +
        experience_score * weights['experience'] +
        education_score * weights['education'] +
        location_score * weights['location']
    )
    
    return {
        'overall_score': round(overall_score, 2),
        'skill_score': round(skill_score, 2),
        'experience_score': round(experience_score, 2),
        'education_score': round(education_score, 2),
        'location_score': round(location_score, 2)
    }

def calculate_skill_match_advanced(candidate_skills: List[str], required_skills: List[str], preferred_skills: List[str] = None) -> float:
    """Advanced skill matching with required vs preferred skills"""
    if not required_skills:
        return 50  # Neutral score if no requirements
    
    preferred_skills = preferred_skills or []
    
    candidate_skills_lower = [skill.lower() for skill in candidate_skills]
    required_skills_lower = [skill.lower() for skill in required_skills]
    preferred_skills_lower = [skill.lower() for skill in preferred_skills]
    
    # Required skills matching (70% weight)
    required_matches = sum(1 for skill in required_skills_lower if skill in candidate_skills_lower)
    required_score = (required_matches / len(required_skills)) * 70
    
    # Preferred skills matching (30% weight)
    preferred_score = 0
    if preferred_skills:
        preferred_matches = sum(1 for skill in preferred_skills_lower if skill in candidate_skills_lower)
        preferred_score = (preferred_matches / len(preferred_skills)) * 30
    else:
        preferred_score = 30  # Full credit if no preferred skills specified
    
    return min(100, required_score + preferred_score)

def rank_candidates_for_job(candidates: List[Dict[str, Any]], job: Dict[str, Any]) -> List[Tuple[Dict[str, Any], Dict[str, float]]]:
    """Rank candidates for a specific job based on match scores"""
    
    candidate_scores = []
    
    for candidate in candidates:
        scores = calculate_overall_match_score(candidate, job)
        candidate_scores.append((candidate, scores))
    
    # Sort by overall score (descending)
    candidate_scores.sort(key=lambda x: x[1]['overall_score'], reverse=True)
    
    return candidate_scores

def recommend_jobs_for_candidate(candidate: Dict[str, Any], jobs: List[Dict[str, Any]], top_n: int = 10) -> List[Tuple[Dict[str, Any], Dict[str, float]]]:
    """Recommend top jobs for a candidate based on match scores"""
    
    job_scores = []
    
    for job in jobs:
        scores = calculate_overall_match_score(candidate, job)
        job_scores.append((job, scores))
    
    # Sort by overall score (descending)
    job_scores.sort(key=lambda x: x[1]['overall_score'], reverse=True)
    
    return job_scores[:top_n]

# Example usage and testing
if __name__ == "__main__":
    # Sample candidate data
    sample_candidate = {
        'contact_info': {
            'email': 'john.doe@email.com',
            'location': 'San Francisco, CA'
        },
        'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker'],
        'experience': [
            {'start_date': '2020', 'end_date': '2024', 'description': 'Senior Software Engineer'},
            {'start_date': '2018', 'end_date': '2020', 'description': 'Software Developer'}
        ],
        'education': [
            {'degree': 'Bachelor of Science in Computer Science', 'year': '2018'}
        ]
    }
    
    # Sample job data
    sample_job = {
        'title': 'Senior Full Stack Developer',
        'required_skills': ['Python', 'React', 'Node.js', 'AWS'],
        'preferred_skills': ['Docker', 'Kubernetes', 'TypeScript'],
        'min_experience': 3,
        'required_degree': 'Bachelor',
        'location': 'San Francisco, CA',
        'remote_ok': True
    }
    
    # Calculate match score
    match_scores = calculate_overall_match_score(sample_candidate, sample_job)
    
    print("Candidate-Job Match Analysis:")
    print(f"Overall Match Score: {match_scores['overall_score']}%")
    print(f"Skills Match: {match_scores['skill_score']}%")
    print(f"Experience Match: {match_scores['experience_score']}%")
    print(f"Education Match: {match_scores['education_score']}%")
    print(f"Location Match: {match_scores['location_score']}%")
