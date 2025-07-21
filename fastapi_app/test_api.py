#!/usr/bin/env python3
"""
Simple API Test Script

Tests basic API functionality to ensure everything is working correctly.
"""

import asyncio
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://localhost:12000"


async def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False


async def test_root_endpoint():
    """Test the root endpoint"""
    print("🔍 Testing root endpoint...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint passed: {data['message']}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False


async def test_docs_endpoint():
    """Test the documentation endpoint"""
    print("🔍 Testing documentation endpoint...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/docs")
        
        if response.status_code == 200:
            print("✅ Documentation endpoint accessible")
            return True
        else:
            print(f"❌ Documentation endpoint failed: {response.status_code}")
            return False


async def test_openapi_schema():
    """Test the OpenAPI schema endpoint"""
    print("🔍 Testing OpenAPI schema...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/openapi.json")
        
        if response.status_code == 200:
            schema = response.json()
            print(f"✅ OpenAPI schema available (version: {schema.get('openapi', 'unknown')})")
            return True
        else:
            print(f"❌ OpenAPI schema failed: {response.status_code}")
            return False


async def test_user_registration():
    """Test user registration endpoint"""
    print("🔍 Testing user registration...")
    
    import time
    timestamp = int(time.time())
    
    user_data = {
        "email": f"test{timestamp}@example.com",
        "username": f"testuser{timestamp}",
        "password": "testpassword123",
        "confirm_password": "testpassword123",
        "user_type": "candidate",
        "phone": "+1234567890"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=user_data
            )
            
            if response.status_code == 201:
                data = response.json()
                print(f"✅ User registration passed: {data.get('email', 'unknown')}")
                return True, user_data
            else:
                print(f"❌ User registration failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False, None
        except Exception as e:
            print(f"❌ User registration error: {e}")
            return False, None


async def test_user_login(email: str = "test@example.com", password: str = "testpassword123"):
    """Test user login endpoint"""
    print("🔍 Testing user login...")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User login passed: {data.get('token_type', 'unknown')} token received")
                return True, data.get('access_token')
            else:
                print(f"❌ User login failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False, None
        except Exception as e:
            print(f"❌ User login error: {e}")
            return False, None


async def test_protected_endpoint(token: str):
    """Test a protected endpoint"""
    print("🔍 Testing protected endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/users/me",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Protected endpoint passed: {data.get('email', 'unknown')}")
                return True
            else:
                print(f"❌ Protected endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Protected endpoint error: {e}")
            return False


async def test_jobs_endpoint():
    """Test jobs listing endpoint"""
    print("🔍 Testing jobs endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/v1/jobs")
            
            if response.status_code == 200:
                data = response.json()
                job_count = len(data.get('jobs', []))
                print(f"✅ Jobs endpoint passed: {job_count} jobs found")
                return True
            else:
                print(f"❌ Jobs endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Jobs endpoint error: {e}")
            return False


async def run_all_tests():
    """Run all API tests"""
    print("🚀 Starting API Tests for Hire Quick FastAPI Application\n")
    
    tests_passed = 0
    total_tests = 0
    
    # Basic endpoint tests
    basic_tests = [
        test_health_check,
        test_root_endpoint,
        test_docs_endpoint,
        test_openapi_schema,
        test_jobs_endpoint
    ]
    
    for test in basic_tests:
        total_tests += 1
        if await test():
            tests_passed += 1
        print()
    
    # Authentication flow tests
    total_tests += 1
    registration_success, user_data = await test_user_registration()
    if registration_success:
        tests_passed += 1
    print()
    
    if registration_success:
        total_tests += 1
        login_success, token = await test_user_login(user_data["email"], user_data["password"])
        if login_success:
            tests_passed += 1
        print()
        
        if login_success and token:
            total_tests += 1
            if await test_protected_endpoint(token):
                tests_passed += 1
            print()
    
    # Summary
    print("=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
    
    print("=" * 50)
    
    return tests_passed == total_tests


async def main():
    """Main test function"""
    try:
        success = await run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())