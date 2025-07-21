"""
AI Service

AI-powered features for resume parsing, job matching, and candidate scoring.
"""

import re
import json
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models.user import User
from ..models.job import Job
from ..models.application import Application

logger = logging.getLogger(__name__)


class AIService:
    """AI-powered recruitment features"""
    
    def __init__(self):
        # Skills database - in production, this would be a more comprehensive database
        self.skills_database = {
            'programming': [
                'python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby',
                'typescript', 'kotlin', 'swift', 'scala', 'r', 'matlab', 'sql'
            ],
            'web_development': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django',
                'flask', 'fastapi', 'spring', 'laravel', 'rails', 'asp.net'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
                'oracle', 'sqlite', 'dynamodb', 'neo4j'
            ],
            'cloud': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible',
                'jenkins', 'gitlab ci', 'github actions'
            ],
            'data_science': [
                'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
                'matplotlib', 'seaborn', 'jupyter', 'spark', 'hadoop'
            ],
            'soft_skills': [
                'leadership', 'communication', 'teamwork', 'problem solving', 'creativity',
                'adaptability', 'time management', 'critical thinking', 'collaboration'
            ]
        }
        
        # Experience level keywords
        self.experience_keywords = {
            'entry': ['entry', 'junior', 'graduate', 'intern', 'trainee', 'associate'],
            'junior': ['junior', '1-2 years', 'associate', 'entry level'],
            'mid': ['mid', 'intermediate', '3-5 years', 'experienced'],
            'senior': ['senior', '5+ years', 'lead', 'principal', 'expert'],
            'lead': ['lead', 'team lead', 'tech lead', 'principal', 'architect'],
            'executive': ['director', 'vp', 'cto', 'ceo', 'head of', 'chief']
        }

    async def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text and extract structured information
        
        Args:
            resume_text: Raw text from resume
            
        Returns:
            Structured resume data
        """
        try:
            parsed_data = {
                'personal_info': self._extract_personal_info(resume_text),
                'skills': self._extract_skills(resume_text),
                'experience': self._extract_experience(resume_text),
                'education': self._extract_education(resume_text),
                'certifications': self._extract_certifications(resume_text),
                'languages': self._extract_languages(resume_text),
                'summary': self._extract_summary(resume_text),
                'experience_level': self._determine_experience_level(resume_text),
                'contact_info': self._extract_contact_info(resume_text)
            }
            
            logger.info(f"Successfully parsed resume with {len(parsed_data['skills'])} skills")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return {'error': str(e)}

    def _extract_personal_info(self, text: str) -> Dict[str, str]:
        """Extract personal information from resume"""
        info = {}
        
        # Extract name (usually first line or after "Name:")
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ['email', 'phone', 'address', 'linkedin']):
                if len(line.split()) >= 2 and len(line) < 50:
                    info['name'] = line
                    break
        
        return info

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information"""
        contact = {}
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact['email'] = emails[0]
        
        # Phone
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.search(linkedin_pattern, text.lower())
        if linkedin:
            contact['linkedin'] = linkedin.group()
        
        return contact

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = set()
        
        # Check all skill categories
        for category, skills in self.skills_database.items():
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.add(skill)
        
        return list(found_skills)

    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience from resume"""
        experience = []
        
        # Look for experience section
        experience_section = self._find_section(text, ['experience', 'work history', 'employment'])
        if not experience_section:
            return experience
        
        # Simple extraction - in production, this would be more sophisticated
        lines = experience_section.split('\n')
        current_job = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_job:
                    experience.append(current_job)
                    current_job = {}
                continue
            
            # Check if line contains dates (simple pattern)
            date_pattern = r'\d{4}|\d{1,2}/\d{4}'
            if re.search(date_pattern, line):
                if 'company' in current_job:
                    current_job['duration'] = line
                else:
                    current_job['title'] = line
            elif not current_job.get('company'):
                current_job['company'] = line
            elif not current_job.get('description'):
                current_job['description'] = line
        
        if current_job:
            experience.append(current_job)
        
        return experience

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        
        education_section = self._find_section(text, ['education', 'academic', 'qualifications'])
        if not education_section:
            return education
        
        # Simple extraction
        lines = education_section.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                education.append({'degree': line})
        
        return education

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_section = self._find_section(text, ['certification', 'certificate', 'licenses'])
        if not cert_section:
            return []
        
        certifications = []
        lines = cert_section.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 5:
                certifications.append(line)
        
        return certifications

    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages"""
        lang_section = self._find_section(text, ['language', 'languages'])
        if not lang_section:
            return []
        
        # Common languages
        languages = ['english', 'spanish', 'french', 'german', 'chinese', 'japanese', 'korean', 'arabic', 'hindi', 'portuguese']
        found_languages = []
        
        for lang in languages:
            if lang in lang_section.lower():
                found_languages.append(lang.title())
        
        return found_languages

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary"""
        summary_section = self._find_section(text, ['summary', 'objective', 'profile', 'about'])
        if summary_section:
            # Return first paragraph
            paragraphs = summary_section.split('\n\n')
            if paragraphs:
                return paragraphs[0].strip()
        
        # If no summary section, return first few lines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if len(line.strip()) > 50 and not any(keyword in line.lower() for keyword in ['email', 'phone', 'address']):
                return line.strip()
        
        return ""

    def _determine_experience_level(self, text: str) -> str:
        """Determine experience level from resume"""
        text_lower = text.lower()
        
        # Count years of experience mentioned
        year_pattern = r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
        years_matches = re.findall(year_pattern, text_lower)
        
        if years_matches:
            max_years = max(int(year) for year in years_matches)
            if max_years < 2:
                return 'entry'
            elif max_years < 4:
                return 'junior'
            elif max_years < 7:
                return 'mid'
            elif max_years < 10:
                return 'senior'
            else:
                return 'lead'
        
        # Check for keywords
        for level, keywords in self.experience_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level
        
        return 'mid'  # Default

    def _find_section(self, text: str, section_names: List[str]) -> str:
        """Find a specific section in the resume"""
        text_lower = text.lower()
        
        for section_name in section_names:
            # Look for section headers
            pattern = rf'^.*{section_name}.*$'
            match = re.search(pattern, text_lower, re.MULTILINE)
            
            if match:
                start_pos = match.end()
                # Find next section or end of text
                next_section_pattern = r'^.*(?:experience|education|skills|certification|project|award|reference).*$'
                next_match = re.search(next_section_pattern, text_lower[start_pos:], re.MULTILINE)
                
                if next_match:
                    end_pos = start_pos + next_match.start()
                    return text[start_pos:end_pos]
                else:
                    return text[start_pos:]
        
        return ""

    async def calculate_job_match_score(self, candidate_skills: List[str], job_requirements: str, job_skills: List[str]) -> float:
        """
        Calculate how well a candidate matches a job
        
        Args:
            candidate_skills: List of candidate skills
            job_requirements: Job requirements text
            job_skills: Required skills for the job
            
        Returns:
            Match score (0-100)
        """
        try:
            if not candidate_skills or not job_skills:
                return 0.0
            
            # Convert to lowercase for comparison
            candidate_skills_lower = [skill.lower() for skill in candidate_skills]
            job_skills_lower = [skill.lower() for skill in job_skills]
            
            # Calculate skill match percentage
            matching_skills = set(candidate_skills_lower) & set(job_skills_lower)
            skill_match_score = (len(matching_skills) / len(job_skills_lower)) * 100
            
            # Bonus for having more skills than required
            bonus_skills = len(set(candidate_skills_lower) - set(job_skills_lower))
            bonus_score = min(bonus_skills * 2, 20)  # Max 20 bonus points
            
            # Calculate requirements match (simple keyword matching)
            requirements_lower = job_requirements.lower()
            requirements_match = 0
            for skill in candidate_skills_lower:
                if skill in requirements_lower:
                    requirements_match += 1
            
            requirements_score = min((requirements_match / len(job_skills_lower)) * 30, 30)
            
            total_score = min(skill_match_score + bonus_score + requirements_score, 100)
            
            logger.info(f"Job match calculated: {total_score:.1f}% (skills: {skill_match_score:.1f}, bonus: {bonus_score}, req: {requirements_score:.1f})")
            return round(total_score, 1)
            
        except Exception as e:
            logger.error(f"Error calculating job match score: {e}")
            return 0.0

    async def get_job_recommendations(self, db: AsyncSession, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get job recommendations for a candidate based on their profile and skills
        
        Args:
            db: Database session
            user_id: Candidate user ID
            limit: Number of recommendations to return
            
        Returns:
            List of recommended jobs with match scores
        """
        try:
            # Get user profile and skills
            user_query = select(User).where(User.id == user_id)
            result = await db.execute(user_query)
            user = result.scalar_one_or_none()
            
            if not user or not user.candidate_profile:
                return []
            
            candidate_skills = user.candidate_profile.get('skills', [])
            if not candidate_skills:
                return []
            
            # Get active jobs
            jobs_query = select(Job).where(Job.status == 'published').limit(50)
            result = await db.execute(jobs_query)
            jobs = result.scalars().all()
            
            recommendations = []
            
            for job in jobs:
                # Calculate match score
                match_score = await self.calculate_job_match_score(
                    candidate_skills,
                    job.requirements,
                    job.skills_required
                )
                
                if match_score > 30:  # Only recommend jobs with >30% match
                    recommendations.append({
                        'job_id': job.id,
                        'job_title': job.title,
                        'company_name': job.company.name if job.company else 'Unknown',
                        'match_score': match_score,
                        'matching_skills': list(set(candidate_skills) & set(job.skills_required)),
                        'location': job.location,
                        'job_type': job.job_type,
                        'salary_range': f"{job.salary_min}-{job.salary_max} {job.currency}" if job.salary_min else None
                    })
            
            # Sort by match score
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting job recommendations: {e}")
            return []

    async def analyze_application_quality(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the quality of a job application
        
        Args:
            application_data: Application data including resume, cover letter, etc.
            
        Returns:
            Analysis results with score and recommendations
        """
        try:
            analysis = {
                'overall_score': 0,
                'components': {},
                'recommendations': [],
                'strengths': [],
                'weaknesses': []
            }
            
            # Analyze resume completeness
            resume_score = self._analyze_resume_completeness(application_data.get('resume_data', {}))
            analysis['components']['resume'] = resume_score
            
            # Analyze cover letter
            cover_letter_score = self._analyze_cover_letter(application_data.get('cover_letter', ''))
            analysis['components']['cover_letter'] = cover_letter_score
            
            # Analyze skill match
            skill_match_score = application_data.get('job_match_score', 0)
            analysis['components']['skill_match'] = skill_match_score
            
            # Calculate overall score
            weights = {'resume': 0.4, 'cover_letter': 0.3, 'skill_match': 0.3}
            analysis['overall_score'] = sum(
                analysis['components'][component] * weight
                for component, weight in weights.items()
            )
            
            # Generate recommendations
            if resume_score < 70:
                analysis['recommendations'].append("Improve resume completeness - add more details about experience and skills")
            
            if cover_letter_score < 60:
                analysis['recommendations'].append("Write a more personalized cover letter that addresses the specific job requirements")
            
            if skill_match_score < 50:
                analysis['recommendations'].append("Consider developing skills that better match the job requirements")
            
            # Identify strengths and weaknesses
            if resume_score >= 80:
                analysis['strengths'].append("Comprehensive resume with detailed experience")
            
            if skill_match_score >= 70:
                analysis['strengths'].append("Strong skill match for the position")
            
            if cover_letter_score < 50:
                analysis['weaknesses'].append("Cover letter needs improvement")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing application quality: {e}")
            return {'error': str(e)}

    def _analyze_resume_completeness(self, resume_data: Dict[str, Any]) -> float:
        """Analyze resume completeness"""
        score = 0
        max_score = 100
        
        # Check for essential sections
        if resume_data.get('personal_info'):
            score += 10
        if resume_data.get('contact_info'):
            score += 15
        if resume_data.get('experience'):
            score += 25
        if resume_data.get('education'):
            score += 15
        if resume_data.get('skills'):
            score += 20
        if resume_data.get('summary'):
            score += 10
        if resume_data.get('certifications'):
            score += 5
        
        return min(score, max_score)

    def _analyze_cover_letter(self, cover_letter: str) -> float:
        """Analyze cover letter quality"""
        if not cover_letter:
            return 0
        
        score = 0
        
        # Length check
        word_count = len(cover_letter.split())
        if word_count >= 100:
            score += 30
        elif word_count >= 50:
            score += 20
        else:
            score += 10
        
        # Personalization indicators
        personal_indicators = ['dear', 'company', 'position', 'role', 'team', 'organization']
        for indicator in personal_indicators:
            if indicator in cover_letter.lower():
                score += 5
        
        # Professional language
        professional_words = ['experience', 'skills', 'qualified', 'contribute', 'achieve', 'successful']
        for word in professional_words:
            if word in cover_letter.lower():
                score += 3
        
        return min(score, 100)

    async def generate_interview_questions(self, job_data: Dict[str, Any], candidate_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate personalized interview questions based on job and candidate
        
        Args:
            job_data: Job information
            candidate_data: Candidate information
            
        Returns:
            List of interview questions with categories
        """
        try:
            questions = []
            
            # Technical questions based on required skills
            job_skills = job_data.get('skills_required', [])
            candidate_skills = candidate_data.get('skills', [])
            
            # Find matching skills for technical questions
            matching_skills = set(job_skills) & set(candidate_skills)
            
            for skill in list(matching_skills)[:3]:  # Limit to 3 technical questions
                questions.append({
                    'category': 'technical',
                    'question': f"Can you describe your experience with {skill} and provide an example of how you've used it in a project?",
                    'skill': skill
                })
            
            # Experience-based questions
            experience_level = candidate_data.get('experience_level', 'mid')
            
            if experience_level in ['senior', 'lead']:
                questions.append({
                    'category': 'leadership',
                    'question': "Tell me about a time when you had to lead a team through a challenging project. How did you handle it?"
                })
            
            questions.append({
                'category': 'experience',
                'question': f"What interests you most about this {job_data.get('title', 'position')} role, and how does it align with your career goals?"
            })
            
            # Behavioral questions
            behavioral_questions = [
                "Describe a situation where you had to solve a complex problem. What was your approach?",
                "Tell me about a time when you had to work with a difficult team member. How did you handle it?",
                "Give me an example of a project where you had to learn something new quickly.",
                "Describe a time when you had to meet a tight deadline. How did you manage your time?"
            ]
            
            # Add 2-3 behavioral questions
            for question in behavioral_questions[:3]:
                questions.append({
                    'category': 'behavioral',
                    'question': question
                })
            
            # Company/role specific questions
            questions.append({
                'category': 'motivation',
                'question': f"Why are you interested in working for {job_data.get('company_name', 'our company')}?"
            })
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating interview questions: {e}")
            return []

    async def score_candidate_response(self, question: str, response: str, expected_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Score a candidate's interview response
        
        Args:
            question: The interview question
            response: Candidate's response
            expected_keywords: Keywords to look for in the response
            
        Returns:
            Scoring analysis
        """
        try:
            if not response or len(response.strip()) < 10:
                return {
                    'score': 0,
                    'feedback': 'Response is too short or empty',
                    'strengths': [],
                    'improvements': ['Provide more detailed responses']
                }
            
            score = 0
            strengths = []
            improvements = []
            
            # Length and detail check
            word_count = len(response.split())
            if word_count >= 100:
                score += 30
                strengths.append('Provided detailed response')
            elif word_count >= 50:
                score += 20
            else:
                score += 10
                improvements.append('Provide more detailed examples')
            
            # Keyword matching
            if expected_keywords:
                response_lower = response.lower()
                matched_keywords = [kw for kw in expected_keywords if kw.lower() in response_lower]
                keyword_score = (len(matched_keywords) / len(expected_keywords)) * 40
                score += keyword_score
                
                if matched_keywords:
                    strengths.append(f'Mentioned relevant concepts: {", ".join(matched_keywords)}')
                else:
                    improvements.append('Include more relevant technical concepts')
            
            # Structure and clarity (simple heuristics)
            sentences = response.split('.')
            if len(sentences) >= 3:
                score += 15
                strengths.append('Well-structured response')
            
            # Professional language indicators
            professional_indicators = ['experience', 'project', 'team', 'challenge', 'solution', 'result', 'learned']
            matched_indicators = [ind for ind in professional_indicators if ind in response.lower()]
            
            if len(matched_indicators) >= 3:
                score += 15
                strengths.append('Used professional language and examples')
            
            score = min(score, 100)
            
            return {
                'score': round(score, 1),
                'feedback': f'Score: {score:.1f}/100',
                'strengths': strengths,
                'improvements': improvements,
                'word_count': word_count
            }
            
        except Exception as e:
            logger.error(f"Error scoring candidate response: {e}")
            return {'error': str(e)}


# Global AI service instance
ai_service = AIService()