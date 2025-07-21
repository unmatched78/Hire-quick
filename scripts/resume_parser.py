import re
import json
import spacy
import PyPDF2
import docx
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import openai
import os

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load spaCy model for NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy English model: python -m spacy download en_core_web_sm")
    nlp = None

class ResumeParser:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.skill_keywords = self._load_skill_keywords()
        self.education_keywords = self._load_education_keywords()
        self.experience_keywords = self._load_experience_keywords()
        
        # Initialize OpenAI if API key is available
        openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def _load_skill_keywords(self) -> Dict[str, List[str]]:
        """Load categorized skill keywords"""
        return {
            'programming_languages': [
                'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Rust',
                'Swift', 'Kotlin', 'TypeScript', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell',
                'PowerShell', 'VBA', 'Assembly', 'Objective-C', 'Dart', 'Elixir', 'Haskell'
            ],
            'web_technologies': [
                'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django', 'Flask',
                'Spring', 'Laravel', 'Ruby on Rails', 'ASP.NET', 'jQuery', 'Bootstrap',
                'Tailwind CSS', 'SASS', 'LESS', 'Webpack', 'Gulp', 'Grunt', 'Next.js',
                'Nuxt.js', 'Svelte', 'Ember.js', 'Backbone.js'
            ],
            'databases': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server',
                'Cassandra', 'DynamoDB', 'Firebase', 'Elasticsearch', 'Neo4j', 'CouchDB',
                'MariaDB', 'InfluxDB', 'Amazon RDS', 'Google Cloud SQL'
            ],
            'cloud_platforms': [
                'AWS', 'Azure', 'Google Cloud Platform', 'GCP', 'Heroku', 'DigitalOcean',
                'Linode', 'Vultr', 'IBM Cloud', 'Oracle Cloud', 'Alibaba Cloud'
            ],
            'devops_tools': [
                'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions', 'Travis CI',
                'CircleCI', 'Ansible', 'Terraform', 'Vagrant', 'Chef', 'Puppet', 'Nagios',
                'Prometheus', 'Grafana', 'ELK Stack', 'Splunk'
            ],
            'data_science': [
                'Machine Learning', 'Deep Learning', 'Data Science', 'AI', 'TensorFlow',
                'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn',
                'Jupyter', 'Apache Spark', 'Hadoop', 'Tableau', 'Power BI', 'D3.js',
                'Plotly', 'Keras', 'OpenCV', 'NLTK', 'spaCy'
            ],
            'mobile_development': [
                'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin', 'Ionic',
                'PhoneGap', 'Cordova', 'Swift', 'Objective-C', 'Kotlin', 'Java'
            ],
            'design_tools': [
                'Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator', 'InDesign',
                'After Effects', 'Premiere Pro', 'Canva', 'InVision', 'Zeplin', 'Marvel'
            ],
            'project_management': [
                'Agile', 'Scrum', 'Kanban', 'JIRA', 'Trello', 'Asana', 'Monday.com',
                'Slack', 'Microsoft Teams', 'Confluence', 'Notion', 'Basecamp'
            ],
            'version_control': [
                'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN', 'Mercurial', 'Perforce'
            ],
            'operating_systems': [
                'Linux', 'Windows', 'macOS', 'Ubuntu', 'CentOS', 'Red Hat', 'Debian',
                'FreeBSD', 'Unix', 'Windows Server'
            ]
        }
    
    def _load_education_keywords(self) -> List[str]:
        """Load education-related keywords"""
        return [
            'Bachelor', 'Master', 'PhD', 'Doctorate', 'Associate', 'Diploma',
            'B.S.', 'B.A.', 'M.S.', 'M.A.', 'MBA', 'M.Tech', 'B.Tech',
            'University', 'College', 'Institute', 'School', 'Academy',
            'Computer Science', 'Engineering', 'Business', 'Mathematics',
            'Physics', 'Chemistry', 'Biology', 'Economics', 'Finance',
            'Marketing', 'Psychology', 'Sociology', 'Literature', 'History'
        ]
    
    def _load_experience_keywords(self) -> List[str]:
        """Load experience-related keywords"""
        return [
            'experience', 'worked', 'developed', 'managed', 'led', 'created',
            'implemented', 'designed', 'built', 'maintained', 'optimized',
            'collaborated', 'coordinated', 'supervised', 'trained', 'mentored',
            'analyzed', 'researched', 'tested', 'deployed', 'integrated'
        ]
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF or DOCX files"""
        text = ""
        file_extension = file_path.lower().split('.')[-1]
        
        try:
            if file_extension == 'pdf':
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            
            elif file_extension in ['docx', 'doc']:
                doc = docx.Document(file_path)
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
            
            elif file_extension == 'txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
            
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
        
        return text.strip()
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume text"""
        contact_info = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone number extraction (multiple formats)
        phone_patterns = [
            r'(\+?1[-.\s]?)?($$)?([0-9]{3})($$)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'(\+?[0-9]{1,3}[-.\s]?)?($$)?([0-9]{3,4})($$)?[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})',
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                # Clean and format phone number
                phone = ''.join(phones[0])
                phone = re.sub(r'[^\d+]', '', phone)
                contact_info['phone'] = phone
                break
        
        # LinkedIn extraction
        linkedin_patterns = [
            r'linkedin\.com/in/[\w-]+',
            r'linkedin\.com/pub/[\w-]+',
            r'www\.linkedin\.com/in/[\w-]+'
        ]
        
        for pattern in linkedin_patterns:
            linkedin = re.findall(pattern, text.lower())
            if linkedin:
                contact_info['linkedin'] = f"https://{linkedin[0]}"
                break
        
        # GitHub extraction
        github_patterns = [
            r'github\.com/[\w-]+',
            r'www\.github\.com/[\w-]+'
        ]
        
        for pattern in github_patterns:
            github = re.findall(pattern, text.lower())
            if github:
                contact_info['github'] = f"https://{github[0]}"
                break
        
        # Website/Portfolio extraction
        website_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        websites = re.findall(website_pattern, text)
        if websites:
            # Filter out LinkedIn and GitHub URLs
            portfolio_sites = [site for site in websites 
                             if 'linkedin.com' not in site.lower() 
                             and 'github.com' not in site.lower()]
            if portfolio_sites:
                contact_info['website'] = portfolio_sites[0]
        
        # Name extraction using NER
        if nlp:
            doc = nlp(text[:1000])  # Process first 1000 characters
            names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            if names:
                contact_info['name'] = names[0]
        
        return contact_info
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract categorized skills from resume text"""
        found_skills = {}
        text_lower = text.lower()
        
        for category, skills in self.skill_keywords.items():
            category_skills = []
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    category_skills.append(skill)
            
            if category_skills:
                found_skills[category] = category_skills
        
        # Extract additional skills using keyword frequency
        words = word_tokenize(text_lower)
        words = [word for word in words if word.isalpha() and word not in self.stop_words]
        word_freq = Counter(words)
        
        # Technical terms that might be skills
        potential_skills = [word for word, freq in word_freq.most_common(50) 
                          if len(word) > 3 and freq > 1]
        
        if potential_skills:
            found_skills['other_skills'] = potential_skills[:10]
        
        return found_skills
    
    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume text"""
        experiences = []
        
        # Split text into sections
        sections = re.split(r'\n\s*\n', text)
        
        # Look for experience sections
        experience_sections = []
        for section in sections:
            section_lower = section.lower()
            if any(keyword in section_lower for keyword in ['experience', 'employment', 'work history', 'career']):
                experience_sections.append(section)
        
        # If no explicit experience section, look for date patterns
        if not experience_sections:
            experience_sections = [text]
        
        for section in experience_sections:
            # Look for date ranges and job titles
            date_patterns = [
                r'(\d{4})\s*[-–]\s*(\d{4}|\w+)',
                r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|\w+)',
                r'(\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|\w+)'
            ]
            
            for pattern in date_patterns:
                matches = re.finditer(pattern, section)
                for match in matches:
                    start_date = match.group(1)
                    end_date = match.group(2)
                    
                    # Extract context around the date (likely job title and company)
                    start_pos = max(0, match.start() - 200)
                    end_pos = min(len(section), match.end() + 200)
                    context = section[start_pos:end_pos]
                    
                    # Try to extract job title and company
                    lines = context.split('\n')
                    job_title = ""
                    company = ""
                    description = ""
                    
                    for i, line in enumerate(lines):
                        line = line.strip()
                        if match.group(0) in line:
                            # Job title is likely before or after the date
                            if i > 0:
                                job_title = lines[i-1].strip()
                            elif i < len(lines) - 1:
                                job_title = lines[i+1].strip()
                            
                            # Company might be on the same line or nearby
                            if '@' in line or 'at ' in line.lower():
                                company_match = re.search(r'(?:@|at\s+)([^,\n]+)', line, re.IGNORECASE)
                                if company_match:
                                    company = company_match.group(1).strip()
                            
                            # Description is the remaining text
                            description = '\n'.join(lines[i+1:i+5]).strip()
                            break
                    
                    if job_title or company:
                        experiences.append({
                            'job_title': job_title,
                            'company': company,
                            'start_date': start_date,
                            'end_date': end_date,
                            'description': description[:500],  # Limit description length
                            'duration': self._calculate_duration(start_date, end_date)
                        })
        
        # Remove duplicates and sort by date
        unique_experiences = []
        seen = set()
        for exp in experiences:
            key = (exp['job_title'], exp['company'], exp['start_date'])
            if key not in seen:
                seen.add(key)
                unique_experiences.append(exp)
        
        return sorted(unique_experiences, key=lambda x: x['start_date'], reverse=True)[:10]
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from resume text"""
        education = []
        
        # Look for degree patterns
        degree_patterns = [
            r'(Bachelor|Master|PhD|Doctorate|Associate|Diploma|B\.S\.|B\.A\.|M\.S\.|M\.A\.|MBA|M\.Tech|B\.Tech)(?:\s+(?:of|in))?\s+([^,\n]+?)(?:\s+from\s+([^,\n]+?))?(?:\s+(?:in\s+)?(\d{4}))?',
            r'(University|College|Institute)(?:\s+of)?\s+([^,\n]+?)(?:\s+(?:in\s+)?(\d{4}))?'
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                
                if 'university' in groups[0].lower() or 'college' in groups[0].lower():
                    # Institution pattern
                    education.append({
                        'institution': match.group(0),
                        'degree': '',
                        'field': '',
                        'year': groups[2] if len(groups) > 2 and groups[2] else ''
                    })
                else:
                    # Degree pattern
                    education.append({
                        'degree': groups[0],
                        'field': groups[1] if len(groups) > 1 and groups[1] else '',
                        'institution': groups[2] if len(groups) > 2 and groups[2] else '',
                        'year': groups[3] if len(groups) > 3 and groups[3] else ''
                    })
        
        return education[:5]  # Return top 5 education entries
    
    def extract_certifications(self, text: str) -> List[Dict[str, str]]:
        """Extract certifications from resume text"""
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r'(AWS|Azure|Google Cloud|GCP)\s+(Certified|Professional|Associate)\s+([^,\n]+)',
            r'(Certified|Professional)\s+([^,\n]+?)(?:\s+(?:from\s+)?([^,\n]+?))?(?:\s+(\d{4}))?',
            r'(PMP|CISSP|CISA|CISM|CEH|OSCP|CCNA|CCNP|CCIE)',
        ]
        
        for pattern in cert_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                cert_name = match.group(0).strip()
                certifications.append({
                    'name': cert_name,
                    'issuer': '',
                    'year': ''
                })
        
        return certifications[:10]
    
    def extract_languages(self, text: str) -> List[Dict[str, str]]:
        """Extract languages from resume text"""
        languages = []
        
        # Common languages
        language_list = [
            'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
            'Chinese', 'Japanese', 'Korean', 'Arabic', 'Russian', 'Hindi',
            'Dutch', 'Swedish', 'Norwegian', 'Danish', 'Finnish'
        ]
        
        proficiency_levels = ['Native', 'Fluent', 'Advanced', 'Intermediate', 'Basic', 'Beginner']
        
        for language in language_list:
            pattern = rf'\b{language}\b(?:\s*[-:]\s*({"|".join(proficiency_levels)}))?'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                proficiency = match.group(1) if match.group(1) else 'Not specified'
                languages.append({
                    'language': language,
                    'proficiency': proficiency
                })
        
        return languages
    
    def _calculate_duration(self, start_date: str, end_date: str) -> str:
        """Calculate duration between two dates"""
        try:
            # Handle different date formats
            if end_date.lower() in ['present', 'current', 'now']:
                end_date = datetime.now().strftime('%Y')
            
            # Extract years
            start_year = int(re.search(r'\d{4}', start_date).group())
            end_year = int(re.search(r'\d{4}', end_date).group())
            
            duration = end_year - start_year
            if duration == 0:
                return "Less than 1 year"
            elif duration == 1:
                return "1 year"
            else:
                return f"{duration} years"
        except:
            return "Unknown"
    
    def calculate_experience_years(self, experiences: List[Dict]) -> float:
        """Calculate total years of experience"""
        total_months = 0
        
        for exp in experiences:
            try:
                start_date = exp['start_date']
                end_date = exp['end_date']
                
                if end_date.lower() in ['present', 'current', 'now']:
                    end_date = datetime.now().strftime('%Y')
                
                start_year = int(re.search(r'\d{4}', start_date).group())
                end_year = int(re.search(r'\d{4}', end_date).group())
                
                total_months += (end_year - start_year) * 12
            except:
                continue
        
        return round(total_months / 12, 1)
    
    def ai_analyze_resume(self, parsed_data: Dict) -> Dict[str, Any]:
        """Use AI to analyze resume and provide insights"""
        if not openai.api_key:
            return {'error': 'OpenAI API key not configured'}
        
        try:
            # Prepare resume summary for AI analysis
            resume_summary = f"""
            Name: {parsed_data.get('contact_info', {}).get('name', 'Unknown')}
            Skills: {', '.join([skill for skills in parsed_data.get('skills', {}).values() for skill in skills])}
            Experience: {len(parsed_data.get('experience', []))} positions
            Education: {len(parsed_data.get('education', []))} entries
            Total Experience: {parsed_data.get('total_experience_years', 0)} years
            """
            
            prompt = f"""
            Analyze this resume and provide insights:
            
            {resume_summary}
            
            Please provide:
            1. Overall assessment (1-10 score)
            2. Key strengths
            3. Areas for improvement
            4. Suitable job roles
            5. Career level (Junior/Mid/Senior)
            
            Format as JSON with keys: score, strengths, improvements, suitable_roles, career_level
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            ai_analysis = json.loads(response.choices[0].message.content)
            return ai_analysis
            
        except Exception as e:
            return {'error': f'AI analysis failed: {str(e)}'}
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Main function to parse resume and extract all information"""
        
        # Extract text from file
        resume_text = self.extract_text_from_file(file_path)
        
        if not resume_text:
            return {'error': 'Could not extract text from file'}
        
        # Extract all information
        parsed_data = {
            'contact_info': self.extract_contact_info(resume_text),
            'skills': self.extract_skills(resume_text),
            'experience': self.extract_experience(resume_text),
            'education': self.extract_education(resume_text),
            'certifications': self.extract_certifications(resume_text),
            'languages': self.extract_languages(resume_text),
            'raw_text': resume_text[:2000],  # Store first 2000 chars for reference
            'file_path': file_path,
            'parsed_at': datetime.now().isoformat()
        }
        
        # Calculate total experience
        parsed_data['total_experience_years'] = self.calculate_experience_years(parsed_data['experience'])
        
        # AI analysis
        parsed_data['ai_analysis'] = self.ai_analyze_resume(parsed_data)
        
        return parsed_data
    
    def calculate_skill_match(self, candidate_skills: Dict[str, List[str]], job_requirements: List[str]) -> Dict[str, Any]:
        """Calculate skill match percentage between candidate and job requirements"""
        if not job_requirements:
            return {'match_percentage': 0.0, 'matched_skills': [], 'missing_skills': job_requirements}
        
        # Flatten candidate skills
        all_candidate_skills = []
        for skills_list in candidate_skills.values():
            all_candidate_skills.extend([skill.lower() for skill in skills_list])
        
        job_requirements_lower = [req.lower().strip() for req in job_requirements]
        
        matched_skills = []
        missing_skills = []
        
        for req in job_requirements_lower:
            if any(req in skill or skill in req for skill in all_candidate_skills):
                matched_skills.append(req)
            else:
                missing_skills.append(req)
        
        match_percentage = (len(matched_skills) / len(job_requirements)) * 100 if job_requirements else 0
        
        return {
            'match_percentage': round(match_percentage, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'total_candidate_skills': len(all_candidate_skills),
            'total_required_skills': len(job_requirements)
        }

# Example usage and testing
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Test with sample resume text
    sample_resume = """
    John Doe
    Software Engineer
    john.doe@email.com
    (555) 123-4567
    linkedin.com/in/johndoe
    github.com/johndoe
    
    EXPERIENCE
    2020 - Present: Senior Software Engineer at TechCorp
    - Developed web applications using React and Node.js
    - Led a team of 5 developers
    - Implemented CI/CD pipelines using Docker and AWS
    
    2018 - 2020: Software Developer at StartupXYZ
    - Built REST APIs using Python and Django
    - Worked with PostgreSQL databases
    - Collaborated with cross-functional teams
    
    EDUCATION
    2018: Bachelor of Science in Computer Science, State University
    
    SKILLS
    Python, JavaScript, React, Node.js, Django, PostgreSQL, AWS, Docker, Git
    
    CERTIFICATIONS
    AWS Certified Solutions Architect - 2021
    
    LANGUAGES
    English - Native
    Spanish - Intermediate
    """
    
    # Parse the sample resume
    parsed = parser.parse_resume_text(sample_resume)
    print(json.dumps(parsed, indent=2))
    
    # Test skill matching
    job_skills = ["Python", "React", "AWS", "Docker", "Machine Learning"]
    match_result = parser.calculate_skill_match(parsed['skills'], job_skills)
    print(f"\nSkill Match Result: {match_result}")
