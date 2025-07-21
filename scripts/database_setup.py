import sqlite3
from datetime import datetime, timedelta
import json
import random

def create_database():
    """Create the recruitment platform database with all necessary tables"""
    
    conn = sqlite3.connect('recruitment_platform.db')
    cursor = conn.cursor()
    
    # Users table (for authentication)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK (user_type IN ('candidate', 'recruiter', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Companies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            website TEXT,
            logo_url TEXT,
            industry TEXT,
            size TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Candidates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            location TEXT,
            linkedin_url TEXT,
            github_url TEXT,
            portfolio_url TEXT,
            resume_url TEXT,
            summary TEXT,
            skills TEXT, -- JSON array of skills
            experience_years INTEGER DEFAULT 0,
            current_title TEXT,
            salary_expectation INTEGER,
            availability TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Recruiters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recruiters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            title TEXT,
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            recruiter_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT, -- JSON array of requirements
            preferred_skills TEXT, -- JSON array of preferred skills
            location TEXT,
            job_type TEXT CHECK (job_type IN ('full-time', 'part-time', 'contract', 'internship')),
            remote_ok BOOLEAN DEFAULT FALSE,
            salary_min INTEGER,
            salary_max INTEGER,
            experience_min INTEGER DEFAULT 0,
            experience_max INTEGER,
            education_required TEXT,
            benefits TEXT, -- JSON array of benefits
            status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'closed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (recruiter_id) REFERENCES recruiters (id)
        )
    ''')
    
    # Applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            status TEXT DEFAULT 'applied' CHECK (status IN ('applied', 'screening', 'interview', 'offer', 'hired', 'rejected')),
            cover_letter TEXT,
            resume_url TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            FOREIGN KEY (candidate_id) REFERENCES candidates (id),
            UNIQUE(job_id, candidate_id)
        )
    ''')
    
    # Interviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            interviewer_id INTEGER NOT NULL,
            interview_type TEXT CHECK (interview_type IN ('phone', 'video', 'in-person', 'technical', 'final')),
            scheduled_at TIMESTAMP NOT NULL,
            duration_minutes INTEGER DEFAULT 60,
            location TEXT,
            meeting_link TEXT,
            status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'rescheduled')),
            feedback TEXT,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications (id),
            FOREIGN KEY (interviewer_id) REFERENCES recruiters (id)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL,
            subject TEXT,
            content TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            application_id INTEGER,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (recipient_id) REFERENCES users (id),
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''')
    
    # Saved jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id),
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            UNIQUE(candidate_id, job_id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs (status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs (location)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_applications_status ON applications (status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications (job_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_applications_candidate_id ON applications (candidate_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_interviews_scheduled_at ON interviews (scheduled_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_recipient_id ON messages (recipient_id)')
    
    conn.commit()
    conn.close()
    
    print("Database created successfully!")

def seed_sample_data():
    """Seed the database with sample data for testing"""
    
    conn = sqlite3.connect('recruitment_platform.db')
    cursor = conn.cursor()
    
    # Sample companies
    companies = [
        ('TechCorp Inc.', 'Leading technology company', 'https://techcorp.com', None, 'Technology', '1000-5000', 'San Francisco, CA'),
        ('StartupXYZ', 'Innovative startup', 'https://startupxyz.com', None, 'Technology', '10-50', 'Remote'),
        ('Design Studio', 'Creative design agency', 'https://designstudio.com', None, 'Design', '50-200', 'New York, NY'),
        ('DataCorp', 'Data analytics company', 'https://datacorp.com', None, 'Analytics', '200-1000', 'Austin, TX'),
        ('CloudTech', 'Cloud infrastructure provider', 'https://cloudtech.com', None, 'Technology', '500-1000', 'Seattle, WA')
    ]
    
    cursor.executemany('''
        INSERT INTO companies (name, description, website, logo_url, industry, size, location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', companies)
    
    # Sample users (recruiters)
    users = [
        ('recruiter1@techcorp.com', 'hashed_password_1', 'recruiter'),
        ('recruiter2@startupxyz.com', 'hashed_password_2', 'recruiter'),
        ('recruiter3@designstudio.com', 'hashed_password_3', 'recruiter'),
        ('candidate1@email.com', 'hashed_password_4', 'candidate'),
        ('candidate2@email.com', 'hashed_password_5', 'candidate')
    ]
    
    cursor.executemany('''
        INSERT INTO users (email, password_hash, user_type)
        VALUES (?, ?, ?)
    ''', users)
    
    # Sample recruiters
    recruiters = [
        (1, 1, 'John', 'Smith', '555-0101', 'Senior Recruiter', 'HR'),
        (2, 2, 'Sarah', 'Johnson', '555-0102', 'Talent Acquisition', 'HR'),
        (3, 3, 'Mike', 'Davis', '555-0103', 'Creative Director', 'Design')
    ]
    
    cursor.executemany('''
        INSERT INTO recruiters (user_id, company_id, first_name, last_name, phone, title, department)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', recruiters)
    
    # Sample candidates
    candidates = [
        (4, 'Alice', 'Johnson', '555-0201', 'San Francisco, CA', 'https://linkedin.com/in/alicejohnson', 
         'https://github.com/alicejohnson', 'https://alicejohnson.dev', None, 
         'Experienced software engineer with 5+ years in full-stack development',
         json.dumps(['Python', 'JavaScript', 'React', 'Node.js', 'AWS']), 5, 'Senior Software Engineer', 150000, 'Immediately'),
        (5, 'Bob', 'Wilson', '555-0202', 'Austin, TX', 'https://linkedin.com/in/bobwilson',
         'https://github.com/bobwilson', None, None,
         'Product manager with expertise in data-driven decision making',
         json.dumps(['Product Strategy', 'Analytics', 'Agile', 'SQL']), 7, 'Senior Product Manager', 140000, '2 weeks notice')
    ]
    
    cursor.executemany('''
        INSERT INTO candidates (user_id, first_name, last_name, phone, location, linkedin_url, 
                               github_url, portfolio_url, resume_url, summary, skills, experience_years, 
                               current_title, salary_expectation, availability)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', candidates)
    
    # Sample jobs
    jobs = [
        (1, 1, 'Senior Software Engineer', 
         'We are looking for a senior software engineer to join our growing team...',
         json.dumps(['Python', 'JavaScript', 'React', 'Node.js']),
         json.dumps(['AWS', 'Docker', 'Kubernetes']),
         'San Francisco, CA', 'full-time', True, 120000, 180000, 3, 10, 'Bachelor',
         json.dumps(['Health Insurance', '401k', 'Stock Options', 'Remote Work']),
         'active', datetime.now() + timedelta(days=30)),
        (2, 2, 'Product Manager',
         'Join our product team to drive innovation and growth...',
         json.dumps(['Product Strategy', 'Analytics', 'Agile']),
         json.dumps(['SQL', 'Python', 'User Research']),
         'Remote', 'full-time', True, 100000, 150000, 3, 8, 'Bachelor',
         json.dumps(['Health Insurance', 'Equity', 'Unlimited PTO']),
         'active', datetime.now() + timedelta(days=45)),
        (3, 3, 'UX Designer',
         'Create beautiful and intuitive user experiences...',
         json.dumps(['Figma', 'User Research', 'Prototyping']),
         json.dumps(['Adobe Creative Suite', 'Sketch', 'InVision']),
         'New York, NY', 'contract', False, 80000, 120000, 2, 6, 'Bachelor',
         json.dumps(['Health Insurance', 'Professional Development']),
         'active', datetime.now() + timedelta(days=60))
    ]
    
    cursor.executemany('''
        INSERT INTO jobs (company_id, recruiter_id, title, description, requirements, preferred_skills,
                         location, job_type, remote_ok, salary_min, salary_max, experience_min, 
                         experience_max, education_required, benefits, status, expires_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', jobs)
    
    # Sample applications
    applications = [
        (1, 1, 'applied', 'I am very interested in this position...', None),
        (2, 2, 'screening', 'Looking forward to contributing to your product team...', None),
        (1, 2, 'interview', 'Excited about the opportunity...', None)
    ]
    
    cursor.executemany('''
        INSERT INTO applications (job_id, candidate_id, status, cover_letter, resume_url)
        VALUES (?, ?, ?, ?, ?)
    ''', applications)
    
    conn.commit()
    conn.close()
    
    print("Sample data seeded successfully!")

if __name__ == "__main__":
    create_database()
    seed_sample_data()
    print("Database setup complete!")
