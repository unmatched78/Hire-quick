"""
OpenAI Service

Enhanced AI features using OpenAI GPT models for advanced recruitment capabilities.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..core.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI-powered recruitment features"""
    
    def __init__(self):
        self.client = None
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 2000
        
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning("OpenAI not available - API key missing or package not installed")

    async def generate_job_description(
        self, 
        job_title: str, 
        company_info: Dict[str, Any], 
        requirements: List[str],
        benefits: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a compelling job description using AI
        
        Args:
            job_title: The job title
            company_info: Company information
            requirements: List of job requirements
            benefits: Optional list of benefits
            
        Returns:
            Generated job description with sections
        """
        if not self.client:
            return self._fallback_job_description(job_title, requirements)
        
        try:
            prompt = f"""
            Create a compelling and professional job description for the following position:

            Job Title: {job_title}
            Company: {company_info.get('name', 'Our Company')}
            Industry: {company_info.get('industry', 'Technology')}
            Company Size: {company_info.get('size', 'Growing startup')}

            Requirements:
            {chr(10).join(f'- {req}' for req in requirements)}

            {f"Benefits: {chr(10).join(f'- {benefit}' for benefit in benefits)}" if benefits else ""}

            Please create a job description with the following sections:
            1. Company Overview (2-3 sentences)
            2. Role Summary (2-3 sentences)
            3. Key Responsibilities (5-7 bullet points)
            4. Required Qualifications (based on provided requirements)
            5. Preferred Qualifications (additional nice-to-have skills)
            6. What We Offer (benefits and perks)
            7. Call to Action (encouraging application)

            Make it engaging, professional, and likely to attract top talent.
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR professional and copywriter specializing in creating compelling job descriptions that attract top talent."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )

            content = response.choices[0].message.content
            
            # Parse the response into sections
            sections = self._parse_job_description(content)
            
            return {
                "job_title": job_title,
                "generated_description": content,
                "sections": sections,
                "word_count": len(content.split()),
                "generated_at": datetime.utcnow().isoformat(),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Error generating job description: {e}")
            return self._fallback_job_description(job_title, requirements)

    async def analyze_resume_advanced(self, resume_text: str, job_description: str = None) -> Dict[str, Any]:
        """
        Advanced resume analysis using OpenAI
        
        Args:
            resume_text: The resume text to analyze
            job_description: Optional job description for matching
            
        Returns:
            Comprehensive resume analysis
        """
        if not self.client:
            return self._fallback_resume_analysis(resume_text)
        
        try:
            prompt = f"""
            Analyze the following resume and provide a comprehensive assessment:

            RESUME:
            {resume_text}

            {f"JOB DESCRIPTION FOR MATCHING: {job_description}" if job_description else ""}

            Please provide analysis in the following JSON format:
            {{
                "overall_score": <score 0-100>,
                "strengths": [<list of key strengths>],
                "weaknesses": [<list of areas for improvement>],
                "skills_extracted": [<list of technical and soft skills>],
                "experience_level": "<entry/junior/mid/senior/executive>",
                "career_progression": "<assessment of career growth>",
                "education_assessment": "<evaluation of educational background>",
                "achievements_highlighted": [<notable achievements>],
                "red_flags": [<any concerns or gaps>],
                "recommendations": [<suggestions for candidate>],
                "job_match_score": <score 0-100 if job description provided>,
                "missing_skills": [<skills needed for job if job description provided>],
                "interview_focus_areas": [<areas to explore in interview>]
            }}
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR professional and resume analyst with 15+ years of experience in talent acquisition and candidate assessment."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )

            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                analysis = self._parse_resume_analysis_text(content)
            
            analysis["analyzed_at"] = datetime.utcnow().isoformat()
            analysis["model_used"] = self.model
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {e}")
            return self._fallback_resume_analysis(resume_text)

    async def generate_interview_questions_advanced(
        self, 
        job_description: str, 
        candidate_resume: str = None,
        interview_type: str = "general",
        difficulty_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate advanced interview questions using AI
        
        Args:
            job_description: The job description
            candidate_resume: Optional candidate resume for personalization
            interview_type: Type of interview (technical, behavioral, cultural, etc.)
            difficulty_level: easy, medium, hard
            
        Returns:
            Generated interview questions with follow-ups
        """
        if not self.client:
            return self._fallback_interview_questions(job_description)
        
        try:
            prompt = f"""
            Generate comprehensive interview questions for the following scenario:

            JOB DESCRIPTION:
            {job_description}

            {f"CANDIDATE RESUME: {candidate_resume}" if candidate_resume else ""}

            Interview Type: {interview_type}
            Difficulty Level: {difficulty_level}

            Please generate questions in the following categories:
            1. Technical Questions (if applicable)
            2. Behavioral Questions (STAR method)
            3. Situational Questions
            4. Cultural Fit Questions
            5. Role-Specific Questions

            For each question, provide:
            - The main question
            - 2-3 follow-up questions
            - What to look for in the answer
            - Red flags to watch out for

            Format as JSON:
            {{
                "interview_type": "{interview_type}",
                "difficulty_level": "{difficulty_level}",
                "estimated_duration": "<minutes>",
                "questions": [
                    {{
                        "category": "<category>",
                        "main_question": "<question>",
                        "follow_ups": [<follow-up questions>],
                        "evaluation_criteria": [<what to look for>],
                        "red_flags": [<warning signs>],
                        "ideal_answer_outline": "<brief outline>"
                    }}
                ],
                "interview_tips": [<tips for interviewer>],
                "closing_questions": [<questions for candidate to ask>]
            }}
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert interview coach and HR professional with extensive experience in conducting effective interviews across various industries and roles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.6
            )

            content = response.choices[0].message.content
            
            try:
                questions = json.loads(content)
            except json.JSONDecodeError:
                questions = self._parse_interview_questions_text(content)
            
            questions["generated_at"] = datetime.utcnow().isoformat()
            questions["model_used"] = self.model
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating interview questions: {e}")
            return self._fallback_interview_questions(job_description)

    async def screen_candidate_application(
        self, 
        job_requirements: str, 
        candidate_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI-powered candidate screening
        
        Args:
            job_requirements: Job requirements and description
            candidate_data: Candidate information including resume, cover letter, etc.
            
        Returns:
            Screening results with recommendations
        """
        if not self.client:
            return self._fallback_screening(candidate_data)
        
        try:
            prompt = f"""
            Screen this candidate application against the job requirements:

            JOB REQUIREMENTS:
            {job_requirements}

            CANDIDATE DATA:
            Resume: {candidate_data.get('resume_text', 'Not provided')}
            Cover Letter: {candidate_data.get('cover_letter', 'Not provided')}
            Skills: {', '.join(candidate_data.get('skills', []))}
            Experience Level: {candidate_data.get('experience_level', 'Not specified')}

            Provide screening results in JSON format:
            {{
                "screening_score": <0-100>,
                "recommendation": "<reject/maybe/interview/strong_candidate>",
                "key_matches": [<requirements that match well>],
                "key_gaps": [<missing requirements>],
                "strengths": [<candidate strengths>],
                "concerns": [<areas of concern>],
                "interview_recommendation": "<yes/no with reasoning>",
                "salary_expectation_fit": "<assessment if salary info available>",
                "cultural_fit_indicators": [<signs of cultural fit>],
                "next_steps": [<recommended actions>],
                "screening_notes": "<detailed notes for recruiter>"
            }}
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert talent acquisition specialist with the ability to quickly and accurately assess candidate fit for positions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.4
            )

            content = response.choices[0].message.content
            
            try:
                screening = json.loads(content)
            except json.JSONDecodeError:
                screening = self._parse_screening_text(content)
            
            screening["screened_at"] = datetime.utcnow().isoformat()
            screening["model_used"] = self.model
            
            return screening
            
        except Exception as e:
            logger.error(f"Error screening candidate: {e}")
            return self._fallback_screening(candidate_data)

    async def generate_personalized_job_recommendations(
        self, 
        candidate_profile: Dict[str, Any], 
        available_jobs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate personalized job recommendations using AI
        
        Args:
            candidate_profile: Candidate's profile and preferences
            available_jobs: List of available job postings
            
        Returns:
            Ranked job recommendations with explanations
        """
        if not self.client or not available_jobs:
            return self._fallback_job_recommendations(candidate_profile, available_jobs)
        
        try:
            # Limit to top 10 jobs to avoid token limits
            jobs_sample = available_jobs[:10]
            
            prompt = f"""
            Analyze this candidate profile and recommend the best matching jobs:

            CANDIDATE PROFILE:
            Skills: {', '.join(candidate_profile.get('skills', []))}
            Experience Level: {candidate_profile.get('experience_level', 'Not specified')}
            Location Preference: {candidate_profile.get('location', 'Not specified')}
            Salary Expectation: {candidate_profile.get('salary_expectation', 'Not specified')}
            Career Goals: {candidate_profile.get('career_goals', 'Not specified')}
            Work Preferences: {candidate_profile.get('work_preferences', 'Not specified')}

            AVAILABLE JOBS:
            {json.dumps(jobs_sample, indent=2)}

            Rank these jobs for this candidate and provide recommendations in JSON format:
            {{
                "recommendations": [
                    {{
                        "job_id": <job_id>,
                        "match_score": <0-100>,
                        "match_reasons": [<why this job matches>],
                        "growth_potential": "<assessment of career growth>",
                        "skill_development": [<skills they can develop>],
                        "potential_concerns": [<any concerns>],
                        "application_advice": "<tips for applying>"
                    }}
                ],
                "overall_market_fit": "<assessment of candidate's market position>",
                "skill_gap_analysis": [<skills to develop for better opportunities>],
                "career_advice": [<general career guidance>]
            }}
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert career counselor and job matching specialist with deep knowledge of various industries and career paths."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.5
            )

            content = response.choices[0].message.content
            
            try:
                recommendations = json.loads(content)
            except json.JSONDecodeError:
                recommendations = self._parse_recommendations_text(content)
            
            recommendations["generated_at"] = datetime.utcnow().isoformat()
            recommendations["model_used"] = self.model
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating job recommendations: {e}")
            return self._fallback_job_recommendations(candidate_profile, available_jobs)

    # Fallback methods for when OpenAI is not available
    def _fallback_job_description(self, job_title: str, requirements: List[str]) -> Dict[str, Any]:
        """Fallback job description generation"""
        return {
            "job_title": job_title,
            "generated_description": f"We are seeking a qualified {job_title} to join our team. Requirements include: {', '.join(requirements)}",
            "sections": {
                "company_overview": "Join our growing company.",
                "role_summary": f"We are looking for a {job_title}.",
                "responsibilities": requirements[:5],
                "qualifications": requirements,
                "benefits": ["Competitive salary", "Health insurance", "Professional development"]
            },
            "fallback": True
        }

    def _fallback_resume_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Fallback resume analysis"""
        return {
            "overall_score": 75,
            "strengths": ["Professional experience", "Relevant skills"],
            "weaknesses": ["Could provide more specific achievements"],
            "skills_extracted": ["Communication", "Problem solving"],
            "experience_level": "mid",
            "fallback": True
        }

    def _fallback_interview_questions(self, job_description: str) -> Dict[str, Any]:
        """Fallback interview questions"""
        return {
            "questions": [
                {
                    "category": "general",
                    "main_question": "Tell me about your relevant experience for this role.",
                    "follow_ups": ["What was your biggest achievement?", "How do you handle challenges?"],
                    "evaluation_criteria": ["Relevant experience", "Communication skills"]
                }
            ],
            "fallback": True
        }

    def _fallback_screening(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback candidate screening"""
        return {
            "screening_score": 70,
            "recommendation": "interview",
            "key_matches": ["Basic qualifications met"],
            "key_gaps": ["Need to verify specific skills"],
            "interview_recommendation": "yes",
            "fallback": True
        }

    def _fallback_job_recommendations(self, candidate_profile: Dict[str, Any], available_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback job recommendations"""
        return {
            "recommendations": [
                {
                    "job_id": job.get("id", 0),
                    "match_score": 60,
                    "match_reasons": ["Basic skill alignment"],
                    "growth_potential": "Good opportunity for growth"
                }
                for job in available_jobs[:3]
            ],
            "fallback": True
        }

    # Helper methods for parsing AI responses
    def _parse_job_description(self, content: str) -> Dict[str, Any]:
        """Parse job description content into sections"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['company overview', 'role summary', 'responsibilities', 'qualifications', 'benefits']):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.lower().replace(':', '').replace(' ', '_')
                current_content = []
            elif line:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

    def _parse_resume_analysis_text(self, content: str) -> Dict[str, Any]:
        """Parse resume analysis from text format"""
        return {
            "overall_score": 75,
            "analysis_text": content,
            "parsed_from_text": True
        }

    def _parse_interview_questions_text(self, content: str) -> Dict[str, Any]:
        """Parse interview questions from text format"""
        return {
            "questions_text": content,
            "parsed_from_text": True
        }

    def _parse_screening_text(self, content: str) -> Dict[str, Any]:
        """Parse screening results from text format"""
        return {
            "screening_text": content,
            "parsed_from_text": True
        }

    def _parse_recommendations_text(self, content: str) -> Dict[str, Any]:
        """Parse job recommendations from text format"""
        return {
            "recommendations_text": content,
            "parsed_from_text": True
        }


# Global OpenAI service instance
openai_service = OpenAIService()