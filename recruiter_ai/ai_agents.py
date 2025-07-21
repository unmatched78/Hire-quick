import openai
from django.conf import settings
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import re

class JobDescriptionAgent:
    """AI Agent for generating job descriptions and requirements"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_job_description(self, job_data):
        """Generate a complete job description based on input parameters"""
        
        prompt = f"""
        Create a comprehensive job description for the following position:
        
        Job Title: {job_data['job_title']}
        Company Industry: {job_data.get('industry', 'Technology')}
        Experience Level: {job_data['experience_level']}
        Employment Type: {job_data['employment_type']}
        Remote Option: {job_data['remote_option']}
        Requirements Input: {job_data['requirements_input']}
        Company Description: {job_data.get('company_description', '')}
        
        Please generate:
        1. A compelling job description (2-3 paragraphs)
        2. Key responsibilities (5-7 bullet points)
        3. Required qualifications (4-6 bullet points)
        4. Preferred qualifications (3-4 bullet points)
        5. Technical skills required (5-8 skills)
        6. Benefits and perks (4-6 items)
        
        Format the response as JSON with the following structure:
        {{
            "description": "Main job description text",
            "responsibilities": ["responsibility 1", "responsibility 2", ...],
            "required_qualifications": ["qualification 1", "qualification 2", ...],
            "preferred_qualifications": ["qualification 1", "qualification 2", ...],
            "technical_skills": ["skill 1", "skill 2", ...],
            "benefits": ["benefit 1", "benefit 2", ...]
        }}
        
        Make the content professional, engaging, and tailored to attract qualified candidates.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert HR professional and job description writer. Create compelling, professional job descriptions that attract top talent."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing if JSON is not properly formatted
                return self._parse_fallback_response(content)
                
        except Exception as e:
            return {
                "error": str(e),
                "description": "Error generating job description. Please try again.",
                "responsibilities": [],
                "required_qualifications": [],
                "preferred_qualifications": [],
                "technical_skills": [],
                "benefits": []
            }
    
    def _parse_fallback_response(self, content):
        """Fallback parser if JSON parsing fails"""
        return {
            "description": "We are seeking a qualified professional to join our team. This role offers excellent opportunities for growth and development in a dynamic environment.",
            "responsibilities": [
                "Execute key job functions effectively",
                "Collaborate with team members",
                "Meet project deadlines and deliverables",
                "Contribute to team goals and objectives"
            ],
            "required_qualifications": [
                "Relevant degree or equivalent experience",
                "Strong communication skills",
                "Problem-solving abilities",
                "Team collaboration skills"
            ],
            "preferred_qualifications": [
                "Previous experience in similar role",
                "Industry certifications",
                "Leadership experience"
            ],
            "technical_skills": [
                "Relevant technical skills",
                "Software proficiency",
                "Industry-specific tools"
            ],
            "benefits": [
                "Competitive salary",
                "Health insurance",
                "Professional development opportunities",
                "Flexible work arrangements"
            ]
        }
    
    def suggest_improvements(self, existing_description):
        """Suggest improvements to an existing job description"""
        
        prompt = f"""
        Please analyze the following job description and suggest 3-5 specific improvements:
        
        {existing_description}
        
        Focus on:
        1. Making it more engaging and attractive to candidates
        2. Improving clarity and structure
        3. Adding missing important elements
        4. Making it more inclusive and diverse
        5. Optimizing for better candidate response
        
        Provide specific, actionable suggestions.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert HR consultant specializing in job description optimization and candidate attraction."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating suggestions: {str(e)}"
    
    def generate_interview_questions(self, job_title, skills, experience_level):
        """Generate interview questions based on job requirements"""
        
        prompt = f"""
        Generate interview questions for a {job_title} position with the following requirements:
        
        Skills: {', '.join(skills) if skills else 'General skills'}
        Experience Level: {experience_level}
        
        Please provide:
        1. 5 behavioral questions
        2. 5 technical questions
        3. 3 situational questions
        4. 2 culture fit questions
        
        Format as JSON:
        {{
            "behavioral": ["question 1", "question 2", ...],
            "technical": ["question 1", "question 2", ...],
            "situational": ["question 1", "question 2", ...],
            "culture_fit": ["question 1", "question 2", ...]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert interviewer and talent acquisition specialist. Create insightful interview questions that help assess candidate fit."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._default_interview_questions()
                
        except Exception as e:
            return self._default_interview_questions()
    
    def _default_interview_questions(self):
        """Default interview questions if AI generation fails"""
        return {
            "behavioral": [
                "Tell me about a challenging project you worked on and how you handled it.",
                "Describe a time when you had to work with a difficult team member.",
                "Give me an example of when you had to learn something new quickly.",
                "Tell me about a time you made a mistake and how you handled it.",
                "Describe a situation where you had to meet a tight deadline."
            ],
            "technical": [
                "Walk me through your approach to solving complex problems.",
                "How do you stay updated with industry trends and technologies?",
                "Describe your experience with relevant tools and technologies.",
                "How do you ensure code quality in your projects?",
                "What's your process for debugging and troubleshooting?"
            ],
            "situational": [
                "How would you handle conflicting priorities from different stakeholders?",
                "What would you do if you disagreed with your manager's approach?",
                "How would you approach a project with unclear requirements?"
            ],
            "culture_fit": [
                "What type of work environment do you thrive in?",
                "How do you prefer to receive feedback?"
            ]
        }

class InterviewSchedulingAgent:
    """AI Agent for intelligent interview scheduling suggestions"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def suggest_interview_structure(self, job_title, experience_level, interview_type):
        """Suggest interview structure and timeline"""
        
        prompt = f"""
        Suggest an optimal interview structure for a {job_title} position:
        
        Experience Level: {experience_level}
        Interview Type: {interview_type}
        
        Please provide:
        1. Recommended interview duration
        2. Interview structure with time allocation
        3. Key areas to focus on
        4. Suggested interview flow
        5. Tips for the interviewer
        
        Format as a structured response.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert interview coach and talent acquisition specialist. Provide structured, actionable interview guidance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating interview structure: {str(e)}"
    
    def generate_email_templates(self, template_type, interview_details=None):
        """Generate email templates for interview communication"""
        
        templates = {
            'interview_invitation': """
Subject: Interview Invitation - {job_title} Position at {company_name}

Dear {candidate_name},

Thank you for your interest in the {job_title} position at {company_name}. We were impressed with your application and would like to invite you for an interview.

Interview Details:
- Date: {interview_date}
- Time: {interview_time}
- Duration: {duration} minutes
- Type: {interview_type}
- Location/Link: {location_or_link}

Please confirm your availability by replying to this email. If you need to reschedule, please let us know as soon as possible.

We look forward to speaking with you!

Best regards,
{interviewer_name}
{company_name}
            """,
            
            'interview_confirmation': """
Subject: Interview Confirmed - {job_title} Position

Dear {candidate_name},

This email confirms your interview for the {job_title} position:

Date & Time: {interview_date} at {interview_time}
Duration: {duration} minutes
Type: {interview_type}
Location/Link: {location_or_link}

Preparation:
{preparation_notes}

If you have any questions or need to make changes, please contact us immediately.

Best regards,
{interviewer_name}
            """,
            
            'interview_reminder': """
Subject: Interview Reminder - Tomorrow at {interview_time}

Dear {candidate_name},

This is a friendly reminder about your interview tomorrow:

Position: {job_title}
Date: {interview_date}
Time: {interview_time}
Type: {interview_type}
Location/Link: {location_or_link}

We look forward to meeting with you!

Best regards,
{interviewer_name}
            """,
            
            'interview_reschedule': """
Subject: Interview Rescheduling - {job_title} Position

Dear {candidate_name},

We need to reschedule your interview for the {job_title} position. We apologize for any inconvenience.

Original: {original_date} at {original_time}
New Options:
- {option_1}
- {option_2}
- {option_3}

Please let us know which option works best for you, or suggest alternative times.

Thank you for your understanding.

Best regards,
{interviewer_name}
            """
        }
        
        return templates.get(template_type, "Template not found")
