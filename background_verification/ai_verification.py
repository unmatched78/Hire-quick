import openai
from django.conf import settings
import cv2
import numpy as np
import pytesseract
from PIL import Image
# import face_recognition
import json
import re
from datetime import datetime
import hashlib
# import magic

class DocumentVerificationAI:
    """AI-powered document verification and analysis"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def analyze_document(self, document_path, document_type):
        """Comprehensive document analysis using AI"""
        try:
            # Extract text using OCR
            extracted_text = self.extract_text_ocr(document_path)
            
            # Analyze document authenticity
            authenticity_score = self.check_document_authenticity(document_path, document_type)
            
            # Extract structured data
            structured_data = self.extract_structured_data(extracted_text, document_type)
            
            # Verify document format and security features
            format_verification = self.verify_document_format(document_path, document_type)
            
            # Generate overall assessment
            assessment = self.generate_document_assessment(
                extracted_text, structured_data, authenticity_score, format_verification
            )
            
            return {
                'extracted_text': extracted_text,
                'structured_data': structured_data,
                'authenticity_score': authenticity_score,
                'format_verification': format_verification,
                'assessment': assessment,
                'quality_score': self.calculate_quality_score(document_path),
                'security_features': self.detect_security_features(document_path),
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'extracted_text': '',
                'structured_data': {},
                'authenticity_score': 0,
                'assessment': 'Error during analysis'
            }
    
    def extract_text_ocr(self, document_path):
        """Extract text from document using OCR"""
        try:
            # Load image
            image = cv2.imread(document_path)
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction and sharpening
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(denoised, config='--psm 6')
            
            return text.strip()
            
        except Exception as e:
            return f"OCR Error: {str(e)}"
    
    def extract_structured_data(self, text, document_type):
        """Extract structured data from document text using AI"""
        
        prompts = {
            'identity': """
            Extract the following information from this identity document text:
            - Full name
            - Date of birth
            - Document number
            - Issue date
            - Expiry date
            - Issuing authority
            - Address (if present)
            
            Text: {text}
            
            Return as JSON format.
            """,
            
            'education_certificate': """
            Extract the following information from this education certificate:
            - Student name
            - Institution name
            - Degree/qualification
            - Field of study
            - Graduation date
            - GPA/Grade (if present)
            - Certificate number
            
            Text: {text}
            
            Return as JSON format.
            """,
            
            'employment_letter': """
            Extract the following information from this employment letter:
            - Employee name
            - Company name
            - Job title/position
            - Employment start date
            - Employment end date (if present)
            - Salary information (if present)
            - Supervisor/HR contact
            
            Text: {text}
            
            Return as JSON format.
            """
        }
        
        prompt = prompts.get(document_type, prompts['identity']).format(text=text)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert document analyst. Extract information accurately and return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {}
                
        except Exception as e:
            return {'error': str(e)}
    
    def check_document_authenticity(self, document_path, document_type):
        """Check document authenticity using AI and image analysis"""
        try:
            # Load image
            image = cv2.imread(document_path)
            
            # Check for common forgery indicators
            authenticity_checks = {
                'image_quality': self.check_image_quality(image),
                'text_consistency': self.check_text_consistency(image),
                'security_features': self.detect_security_features(document_path),
                'metadata_analysis': self.analyze_image_metadata(document_path),
            }
            
            # Calculate overall authenticity score
            scores = [check for check in authenticity_checks.values() if isinstance(check, (int, float))]
            if scores:
                authenticity_score = sum(scores) / len(scores)
            else:
                authenticity_score = 50  # Default neutral score
            
            return min(100, max(0, int(authenticity_score)))
            
        except Exception as e:
            return 0
    
    def check_image_quality(self, image):
        """Check image quality indicators"""
        try:
            # Calculate image sharpness using Laplacian variance
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize to 0-100 scale
            quality_score = min(100, laplacian_var / 10)
            
            return quality_score
            
        except:
            return 50
    
    def check_text_consistency(self, image):
        """Check for text consistency and potential tampering"""
        try:
            # Extract text regions
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Find text regions using contours
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze text region consistency
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 20 and h > 10:  # Filter small regions
                    text_regions.append((x, y, w, h))
            
            # Check for consistent font sizes and alignments
            if len(text_regions) > 1:
                heights = [region[3] for region in text_regions]
                height_consistency = 100 - (np.std(heights) / np.mean(heights) * 100)
                return max(0, min(100, height_consistency))
            
            return 75  # Default score for single or no text regions
            
        except:
            return 50
    
    def detect_security_features(self, document_path):
        """Detect security features in documents"""
        try:
            image = cv2.imread(document_path)
            
            security_features = {
                'watermarks': self.detect_watermarks(image),
                'holograms': self.detect_holograms(image),
                'microtext': self.detect_microtext(image),
                'security_threads': self.detect_security_threads(image),
            }
            
            return security_features
            
        except:
            return {}
    
    def detect_watermarks(self, image):
        """Detect watermarks in document"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply different filters to detect watermarks
            # This is a simplified detection - real watermark detection is more complex
            blurred = cv2.GaussianBlur(gray, (15, 15), 0)
            diff = cv2.absdiff(gray, blurred)
            
            # Check for watermark patterns
            watermark_score = np.mean(diff)
            
            return {
                'detected': watermark_score > 10,
                'confidence': min(100, watermark_score * 2)
            }
            
        except:
            return {'detected': False, 'confidence': 0}
    
    def detect_holograms(self, image):
        """Detect holographic elements"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Look for iridescent colors typical of holograms
            # This is a simplified approach
            saturation = hsv[:, :, 1]
            high_saturation = np.sum(saturation > 200)
            
            total_pixels = image.shape[0] * image.shape[1]
            hologram_ratio = high_saturation / total_pixels
            
            return {
                'detected': hologram_ratio > 0.01,
                'confidence': min(100, hologram_ratio * 1000)
            }
            
        except:
            return {'detected': False, 'confidence': 0}
    
    def detect_microtext(self, image):
        """Detect microtext in documents"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Look for very small text patterns
            kernel = np.ones((2, 2), np.uint8)
            processed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # Find small contours that might be microtext
            contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            small_contours = [c for c in contours if cv2.contourArea(c) < 50]
            
            return {
                'detected': len(small_contours) > 100,
                'confidence': min(100, len(small_contours) / 10)
            }
            
        except:
            return {'detected': False, 'confidence': 0}
    
    def detect_security_threads(self, image):
        """Detect security threads in documents"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Look for thin vertical or horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
            
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
            
            thread_score = np.sum(horizontal_lines) + np.sum(vertical_lines)
            
            return {
                'detected': thread_score > 1000000,
                'confidence': min(100, thread_score / 100000)
            }
            
        except:
            return {'detected': False, 'confidence': 0}
    
    def analyze_image_metadata(self, document_path):
        """Analyze image metadata for tampering indicators"""
        try:
            # This would typically involve EXIF data analysis
            # For now, return basic file information
            with open(document_path, 'rb') as f:
                file_content = f.read()
                file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Check file type
            file_type = magic.from_file(document_path, mime=True)
            
            return {
                'file_hash': file_hash,
                'file_type': file_type,
                'file_size': len(file_content),
                'tampering_indicators': []  # Would be populated with actual analysis
            }
            
        except:
            return {}
    
    def calculate_quality_score(self, document_path):
        """Calculate overall document quality score"""
        try:
            image = cv2.imread(document_path)
            
            # Multiple quality metrics
            quality_metrics = {
                'sharpness': self.check_image_quality(image),
                'brightness': self.check_brightness(image),
                'contrast': self.check_contrast(image),
                'resolution': self.check_resolution(image),
            }
            
            # Calculate weighted average
            weights = {'sharpness': 0.4, 'brightness': 0.2, 'contrast': 0.2, 'resolution': 0.2}
            quality_score = sum(quality_metrics[metric] * weights[metric] for metric in quality_metrics)
            
            return int(quality_score)
            
        except:
            return 50
    
    def check_brightness(self, image):
        """Check image brightness"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # Optimal brightness is around 127 (middle of 0-255 range)
            brightness_score = 100 - abs(brightness - 127) / 127 * 100
            
            return max(0, brightness_score)
            
        except:
            return 50
    
    def check_contrast(self, image):
        """Check image contrast"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            contrast = gray.std()
            
            # Higher standard deviation indicates better contrast
            contrast_score = min(100, contrast * 2)
            
            return contrast_score
            
        except:
            return 50
    
    def check_resolution(self, image):
        """Check image resolution adequacy"""
        try:
            height, width = image.shape[:2]
            total_pixels = height * width
            
            # Score based on total pixels (higher is better up to a point)
            if total_pixels < 100000:  # Less than 0.1MP
                resolution_score = total_pixels / 1000
            elif total_pixels < 2000000:  # Less than 2MP
                resolution_score = 100
            else:  # Very high resolution might indicate scanning artifacts
                resolution_score = max(80, 100 - (total_pixels - 2000000) / 100000)
            
            return min(100, resolution_score)
            
        except:
            return 50
    
    def generate_document_assessment(self, extracted_text, structured_data, authenticity_score, format_verification):
        """Generate AI-powered assessment of document"""
        
        prompt = f"""
        Analyze this document verification data and provide a comprehensive assessment:
        
        Extracted Text: {extracted_text[:500]}...
        Structured Data: {json.dumps(structured_data, indent=2)}
        Authenticity Score: {authenticity_score}/100
        Format Verification: {json.dumps(format_verification, indent=2)}
        
        Please provide:
        1. Overall assessment (ACCEPT/REVIEW/REJECT)
        2. Key findings
        3. Risk factors identified
        4. Recommendations for manual review
        5. Confidence level (0-100)
        
        Format as structured text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert document verification analyst. Provide thorough, accurate assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Assessment generation failed: {str(e)}"

class BackgroundCheckAI:
    """AI-powered background check analysis and risk assessment"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def analyze_criminal_record(self, criminal_data):
        """Analyze criminal record data for risk assessment"""
        
        prompt = f"""
        Analyze this criminal background check data and provide a risk assessment:
        
        Criminal Record Data: {json.dumps(criminal_data, indent=2)}
        
        Please provide:
        1. Risk level (LOW/MEDIUM/HIGH/CRITICAL)
        2. Risk factors identified
        3. Relevance to employment
        4. Recommendations
        5. Legal considerations
        6. Risk score (0-100)
        
        Consider factors like:
        - Nature of offenses
        - Recency of incidents
        - Pattern of behavior
        - Relevance to job role
        - Rehabilitation indicators
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert risk analyst specializing in employment background checks. Provide fair, unbiased assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Criminal record analysis failed: {str(e)}"
    
    def analyze_employment_verification(self, employment_data):
        """Analyze employment verification discrepancies"""
        
        prompt = f"""
        Analyze this employment verification data for discrepancies:
        
        Employment Data: {json.dumps(employment_data, indent=2)}
        
        Identify:
        1. Any discrepancies found
        2. Severity of discrepancies
        3. Possible explanations
        4. Impact on hiring decision
        5. Recommendations for follow-up
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert employment verification analyst. Identify discrepancies and assess their significance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Employment verification analysis failed: {str(e)}"
    
    def generate_overall_assessment(self, all_check_results):
        """Generate overall background check assessment"""
        
        prompt = f"""
        Based on all background check results, provide an overall assessment:
        
        All Check Results: {json.dumps(all_check_results, indent=2)}
        
        Provide:
        1. Overall recommendation (CLEAR/CONSIDER/SUSPENDED)
        2. Key risk factors
        3. Positive indicators
        4. Areas requiring attention
        5. Hiring recommendation with rationale
        6. Legal compliance notes
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior background check analyst. Provide comprehensive, fair assessments that help employers make informed decisions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Overall assessment generation failed: {str(e)}"
