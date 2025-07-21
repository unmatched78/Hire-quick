"""
File Handler Utilities

File upload, processing, and management utilities.
"""

import os
import uuid
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import aiofiles
from fastapi import UploadFile, HTTPException
import logging
from PIL import Image
import PyPDF2
import docx
import magic

logger = logging.getLogger(__name__)


class FileHandler:
    """File handling utilities"""
    
    def __init__(self, upload_dir: str = "media/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Allowed file types
        self.allowed_image_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'
        }
        self.allowed_document_types = {
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'text/rtf'
        }
        self.allowed_video_types = {
            'video/mp4', 'video/avi', 'video/mov', 'video/wmv'
        }
        
        # File size limits (in bytes)
        self.max_image_size = 5 * 1024 * 1024  # 5MB
        self.max_document_size = 10 * 1024 * 1024  # 10MB
        self.max_video_size = 100 * 1024 * 1024  # 100MB

    async def upload_file(
        self,
        file: UploadFile,
        file_type: str = "document",
        user_id: Optional[int] = None,
        subfolder: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file and return file information
        
        Args:
            file: The uploaded file
            file_type: Type of file (image, document, video)
            user_id: User ID for organizing files
            subfolder: Additional subfolder for organization
            
        Returns:
            File information dictionary
        """
        try:
            # Validate file
            validation_result = await self._validate_file(file, file_type)
            if not validation_result['valid']:
                raise HTTPException(status_code=400, detail=validation_result['error'])
            
            # Generate unique filename
            file_extension = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create directory structure
            save_dir = self.upload_dir / file_type
            if user_id:
                save_dir = save_dir / str(user_id)
            if subfolder:
                save_dir = save_dir / subfolder
            
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = save_dir / unique_filename
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Get file info
            file_info = {
                'filename': unique_filename,
                'original_filename': file.filename,
                'file_path': str(file_path),
                'file_url': f"/{file_path.relative_to(self.upload_dir.parent)}",
                'file_size': len(content),
                'mime_type': file.content_type,
                'file_type': file_type
            }
            
            # Process file based on type
            if file_type == 'image':
                file_info.update(await self._process_image(file_path))
            elif file_type == 'document':
                file_info.update(await self._process_document(file_path))
            
            logger.info(f"File uploaded successfully: {unique_filename}")
            return file_info
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    async def _validate_file(self, file: UploadFile, file_type: str) -> Dict[str, Any]:
        """Validate uploaded file"""
        try:
            # Check if file exists
            if not file or not file.filename:
                return {'valid': False, 'error': 'No file provided'}
            
            # Read file content for validation
            content = await file.read()
            file_size = len(content)
            
            # Reset file pointer
            await file.seek(0)
            
            # Validate file size
            max_size = self._get_max_file_size(file_type)
            if file_size > max_size:
                return {
                    'valid': False,
                    'error': f'File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)'
                }
            
            # Validate MIME type
            allowed_types = self._get_allowed_types(file_type)
            
            # Use python-magic for more accurate MIME type detection
            try:
                detected_mime = magic.from_buffer(content, mime=True)
            except:
                detected_mime = file.content_type
            
            if detected_mime not in allowed_types and file.content_type not in allowed_types:
                return {
                    'valid': False,
                    'error': f'File type not allowed. Allowed types: {", ".join(allowed_types)}'
                }
            
            # Additional security checks
            if not self._is_safe_filename(file.filename):
                return {'valid': False, 'error': 'Invalid filename'}
            
            return {'valid': True}
            
        except Exception as e:
            logger.error(f"Error validating file: {e}")
            return {'valid': False, 'error': 'File validation failed'}

    def _get_max_file_size(self, file_type: str) -> int:
        """Get maximum file size for file type"""
        size_map = {
            'image': self.max_image_size,
            'document': self.max_document_size,
            'video': self.max_video_size
        }
        return size_map.get(file_type, self.max_document_size)

    def _get_allowed_types(self, file_type: str) -> set:
        """Get allowed MIME types for file type"""
        type_map = {
            'image': self.allowed_image_types,
            'document': self.allowed_document_types,
            'video': self.allowed_video_types
        }
        return type_map.get(file_type, self.allowed_document_types)

    def _is_safe_filename(self, filename: str) -> bool:
        """Check if filename is safe"""
        # Basic security checks
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        return not any(char in filename for char in dangerous_chars)

    async def _process_image(self, file_path: Path) -> Dict[str, Any]:
        """Process uploaded image"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                
                # Create thumbnail
                thumbnail_path = file_path.parent / f"thumb_{file_path.name}"
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(thumbnail_path, optimize=True, quality=85)
                
                return {
                    'width': width,
                    'height': height,
                    'thumbnail_url': f"/{thumbnail_path.relative_to(self.upload_dir.parent)}",
                    'has_thumbnail': True
                }
                
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {'has_thumbnail': False}

    async def _process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process uploaded document"""
        try:
            doc_info = {'text_content': '', 'page_count': 0}
            
            if file_path.suffix.lower() == '.pdf':
                doc_info.update(await self._extract_pdf_content(file_path))
            elif file_path.suffix.lower() in ['.doc', '.docx']:
                doc_info.update(await self._extract_docx_content(file_path))
            elif file_path.suffix.lower() == '.txt':
                doc_info.update(await self._extract_text_content(file_path))
            
            return doc_info
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return {'text_content': '', 'page_count': 0}

    async def _extract_pdf_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract text content from PDF"""
        try:
            text_content = ""
            page_count = 0
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            
            return {
                'text_content': text_content.strip(),
                'page_count': page_count
            }
            
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            return {'text_content': '', 'page_count': 0}

    async def _extract_docx_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract text content from DOCX"""
        try:
            doc = docx.Document(file_path)
            text_content = ""
            
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            
            return {
                'text_content': text_content.strip(),
                'page_count': 1  # DOCX doesn't have clear page boundaries
            }
            
        except Exception as e:
            logger.error(f"Error extracting DOCX content: {e}")
            return {'text_content': '', 'page_count': 0}

    async def _extract_text_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract content from text file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                text_content = await file.read()
            
            return {
                'text_content': text_content.strip(),
                'page_count': 1
            }
            
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return {'text_content': '', 'page_count': 0}

    async def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                
                # Also delete thumbnail if it exists
                if path.name.startswith('thumb_'):
                    pass  # It's already a thumbnail
                else:
                    thumbnail_path = path.parent / f"thumb_{path.name}"
                    if thumbnail_path.exists():
                        thumbnail_path.unlink()
                
                logger.info(f"File deleted: {file_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            mime_type, _ = mimetypes.guess_type(str(path))
            
            return {
                'filename': path.name,
                'file_path': str(path),
                'file_size': stat.st_size,
                'mime_type': mime_type,
                'created_at': stat.st_ctime,
                'modified_at': stat.st_mtime
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None

    async def create_zip_archive(self, files: List[str], archive_name: str) -> Optional[str]:
        """Create a ZIP archive from multiple files"""
        try:
            import zipfile
            
            archive_path = self.upload_dir / "archives" / f"{archive_name}.zip"
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    path = Path(file_path)
                    if path.exists():
                        zipf.write(path, path.name)
            
            logger.info(f"ZIP archive created: {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"Error creating ZIP archive: {e}")
            return None

    def get_file_url(self, file_path: str, base_url: str = "") -> str:
        """Get public URL for a file"""
        path = Path(file_path)
        relative_path = path.relative_to(self.upload_dir.parent)
        return f"{base_url}/{relative_path}"

    async def cleanup_old_files(self, days_old: int = 30) -> int:
        """Clean up files older than specified days"""
        try:
            import time
            
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            for file_path in self.upload_dir.rglob('*'):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Error deleting old file {file_path}: {e}")
            
            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0


# Global file handler instance
file_handler = FileHandler()