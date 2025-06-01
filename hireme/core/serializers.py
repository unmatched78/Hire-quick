from rest_framework import serializers
from .models import User, JobSeeker, Company, Job, Application, Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type']

class JobSeekerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = JobSeeker
        fields = ['id', 'user', 'resume', 'skills', 'experience', 'preferences']

class CompanySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Company
        fields = ['id', 'user', 'name', 'description', 'location', 'industry', 'culture']

class JobSerializer(serializers.ModelSerializer):
    posted_by = CompanySerializer(read_only=True)
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'salary_min', 'salary_max', 'job_type', 'posted_by', 'date_posted']

class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    applicant = JobSeekerSerializer(read_only=True)
    class Meta:
        model = Application
        fields = ['id', 'job', 'applicant', 'status', 'date_applied']

class ReviewSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    reviewer = JobSeekerSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'company', 'reviewer', 'rating', 'comment', 'date']