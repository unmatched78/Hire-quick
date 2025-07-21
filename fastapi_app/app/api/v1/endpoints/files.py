"""
File Management API Endpoints

File upload, processing, and management endpoints.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
from pathlib import Path

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....utils.file_handler import file_handler

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    file_type: str = Form("document", regex="^(image|document|video)$", description="Type of file"),
    subfolder: Optional[str] = Form(None, description="Optional subfolder for organization"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Upload a file to the server
    
    Supports images, documents, and videos with automatic processing and validation.
    """
    try:
        # Upload and process the file
        file_info = await file_handler.upload_file(
            file,
            file_type=file_type,
            user_id=current_user.id,
            subfolder=subfolder
        )
        
        return {
            "message": "File uploaded successfully",
            "file_info": file_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.post("/upload/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="Files to upload"),
    file_type: str = Form("document", regex="^(image|document|video)$", description="Type of files"),
    subfolder: Optional[str] = Form(None, description="Optional subfolder for organization"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Upload multiple files to the server
    
    Batch upload with individual file processing and validation.
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per upload")
    
    try:
        uploaded_files = []
        failed_files = []
        
        for file in files:
            try:
                file_info = await file_handler.upload_file(
                    file,
                    file_type=file_type,
                    user_id=current_user.id,
                    subfolder=subfolder
                )
                uploaded_files.append(file_info)
            except Exception as e:
                failed_files.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return {
            "message": f"Uploaded {len(uploaded_files)} files successfully",
            "uploaded_files": uploaded_files,
            "failed_files": failed_files,
            "total_uploaded": len(uploaded_files),
            "total_failed": len(failed_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload files: {str(e)}")


@router.post("/upload/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(..., description="Profile picture to upload"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload and set user profile picture
    
    Uploads an image file and sets it as the user's profile picture.
    """
    try:
        # Upload the image
        file_info = await file_handler.upload_file(
            file,
            file_type="image",
            user_id=current_user.id,
            subfolder="profile_pictures"
        )
        
        # Update user profile with new picture URL
        if current_user.user_type == 'candidate':
            if not current_user.candidate_profile:
                current_user.candidate_profile = {}
            current_user.candidate_profile['profile_picture_url'] = file_info['file_url']
        else:
            if not current_user.recruiter_profile:
                current_user.recruiter_profile = {}
            current_user.recruiter_profile['profile_picture_url'] = file_info['file_url']
        
        await db.commit()
        
        return {
            "message": "Profile picture uploaded successfully",
            "profile_picture_url": file_info['file_url'],
            "file_info": file_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload profile picture: {str(e)}")


@router.post("/upload/resume")
async def upload_resume(
    file: UploadFile = File(..., description="Resume file to upload"),
    parse_resume: bool = Form(True, description="Whether to parse the resume with AI"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload and optionally parse a resume
    
    Uploads a resume file and optionally parses it with AI to extract information.
    """
    if current_user.user_type != 'candidate':
        raise HTTPException(status_code=403, detail="Only candidates can upload resumes")
    
    try:
        # Upload the resume
        file_info = await file_handler.upload_file(
            file,
            file_type="document",
            user_id=current_user.id,
            subfolder="resumes"
        )
        
        # Update user profile with resume URL
        if not current_user.candidate_profile:
            current_user.candidate_profile = {}
        current_user.candidate_profile['resume_url'] = file_info['file_url']
        
        result = {
            "message": "Resume uploaded successfully",
            "resume_url": file_info['file_url'],
            "file_info": file_info
        }
        
        # Parse resume if requested
        if parse_resume and file_info.get('text_content'):
            from ....services.ai_service import ai_service
            
            parsed_data = await ai_service.parse_resume(file_info['text_content'])
            
            if 'error' not in parsed_data:
                # Update user profile with parsed data
                current_user.candidate_profile.update({
                    'skills': parsed_data.get('skills', []),
                    'experience_level': parsed_data.get('experience_level', 'mid'),
                    'parsed_resume_data': parsed_data
                })
                
                result['parsed_data'] = parsed_data
                result['message'] = "Resume uploaded and parsed successfully"
        
        await db.commit()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload resume: {str(e)}")


@router.get("/download/{file_path:path}")
async def download_file(
    file_path: str,
    current_user: User = Depends(get_current_user)
) -> FileResponse:
    """
    Download a file by its path
    
    Returns the file for download if the user has permission to access it.
    """
    try:
        # Security check: ensure the file belongs to the user or they have permission
        if not file_path.startswith(f"media/uploads/document/{current_user.id}/") and \
           not file_path.startswith(f"media/uploads/image/{current_user.id}/") and \
           current_user.user_type != 'admin':
            raise HTTPException(status_code=403, detail="Access denied")
        
        full_path = Path(file_path)
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(full_path),
            filename=full_path.name,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")


@router.delete("/delete")
async def delete_file(
    file_path: str = Query(..., description="Path of file to delete"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete a file
    
    Removes a file from the server if the user has permission.
    """
    try:
        # Security check: ensure the file belongs to the user or they have permission
        if not file_path.startswith(f"media/uploads/document/{current_user.id}/") and \
           not file_path.startswith(f"media/uploads/image/{current_user.id}/") and \
           current_user.user_type != 'admin':
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await file_handler.delete_file(file_path)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found or could not be deleted")
        
        return {
            "message": "File deleted successfully",
            "file_path": file_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.get("/info")
async def get_file_info(
    file_path: str = Query(..., description="Path of file to get info for"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get information about a file
    
    Returns metadata and information about a file.
    """
    try:
        # Security check
        if not file_path.startswith(f"media/uploads/document/{current_user.id}/") and \
           not file_path.startswith(f"media/uploads/image/{current_user.id}/") and \
           current_user.user_type != 'admin':
            raise HTTPException(status_code=403, detail="Access denied")
        
        file_info = await file_handler.get_file_info(file_path)
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "file_info": file_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")


@router.get("/list")
async def list_user_files(
    file_type: Optional[str] = Query(None, regex="^(image|document|video)$", description="Filter by file type"),
    subfolder: Optional[str] = Query(None, description="Filter by subfolder"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    List files uploaded by the current user
    
    Returns a list of files uploaded by the user with optional filtering.
    """
    try:
        user_upload_dir = Path(f"media/uploads")
        files = []
        
        # Search in user's directories
        search_dirs = []
        if file_type:
            search_dirs.append(user_upload_dir / file_type / str(current_user.id))
        else:
            for ft in ['image', 'document', 'video']:
                search_dirs.append(user_upload_dir / ft / str(current_user.id))
        
        for search_dir in search_dirs:
            if search_dir.exists():
                if subfolder:
                    search_dir = search_dir / subfolder
                    if not search_dir.exists():
                        continue
                
                for file_path in search_dir.rglob('*'):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        file_info = await file_handler.get_file_info(str(file_path))
                        if file_info:
                            files.append(file_info)
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x.get('modified_at', 0), reverse=True)
        
        return {
            "files": files,
            "total_files": len(files),
            "file_type_filter": file_type,
            "subfolder_filter": subfolder
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@router.post("/create-archive")
async def create_file_archive(
    file_paths: List[str] = Form(..., description="List of file paths to include in archive"),
    archive_name: str = Form(..., description="Name for the archive file"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a ZIP archive from multiple files
    
    Creates a downloadable ZIP archive containing the specified files.
    """
    try:
        # Security check: ensure all files belong to the user
        for file_path in file_paths:
            if not file_path.startswith(f"media/uploads/document/{current_user.id}/") and \
               not file_path.startswith(f"media/uploads/image/{current_user.id}/") and \
               current_user.user_type != 'admin':
                raise HTTPException(status_code=403, detail=f"Access denied to file: {file_path}")
        
        # Create the archive
        archive_path = await file_handler.create_zip_archive(file_paths, archive_name)
        
        if not archive_path:
            raise HTTPException(status_code=500, detail="Failed to create archive")
        
        return {
            "message": "Archive created successfully",
            "archive_path": archive_path,
            "archive_name": f"{archive_name}.zip",
            "files_included": len(file_paths)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create archive: {str(e)}")


@router.get("/storage-usage")
async def get_storage_usage(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get storage usage statistics for the current user
    
    Returns information about file storage usage and limits.
    """
    try:
        user_upload_dir = Path(f"media/uploads")
        total_size = 0
        file_count = 0
        file_types = {"image": 0, "document": 0, "video": 0}
        
        # Calculate storage usage
        for file_type in ['image', 'document', 'video']:
            type_dir = user_upload_dir / file_type / str(current_user.id)
            if type_dir.exists():
                for file_path in type_dir.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        file_count += 1
                        file_types[file_type] += 1
        
        # Storage limits (in bytes)
        storage_limit = 1024 * 1024 * 1024  # 1GB default limit
        if current_user.user_type == 'recruiter':
            storage_limit = 5 * 1024 * 1024 * 1024  # 5GB for recruiters
        
        usage_percentage = (total_size / storage_limit) * 100 if storage_limit > 0 else 0
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_files": file_count,
            "file_types": file_types,
            "storage_limit_bytes": storage_limit,
            "storage_limit_mb": round(storage_limit / (1024 * 1024), 2),
            "usage_percentage": round(usage_percentage, 2),
            "remaining_bytes": max(0, storage_limit - total_size),
            "remaining_mb": round(max(0, storage_limit - total_size) / (1024 * 1024), 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get storage usage: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_files(
    days_old: int = Form(30, ge=1, le=365, description="Delete files older than this many days"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clean up old files for the current user
    
    Removes files older than the specified number of days.
    """
    try:
        import time
        from pathlib import Path
        
        user_upload_dir = Path(f"media/uploads")
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        deleted_size = 0
        
        # Clean up user's files
        for file_type in ['image', 'document', 'video']:
            type_dir = user_upload_dir / file_type / str(current_user.id)
            if type_dir.exists():
                for file_path in type_dir.rglob('*'):
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            deleted_count += 1
                            deleted_size += file_size
                        except Exception as e:
                            # Log error but continue cleanup
                            pass
        
        return {
            "message": f"Cleaned up {deleted_count} old files",
            "deleted_files": deleted_count,
            "deleted_size_bytes": deleted_size,
            "deleted_size_mb": round(deleted_size / (1024 * 1024), 2),
            "days_old": days_old
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup files: {str(e)}")