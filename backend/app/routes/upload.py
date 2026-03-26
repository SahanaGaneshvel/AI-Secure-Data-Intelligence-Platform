"""
File upload endpoint for binary file processing
Handles: .txt, .log, .pdf, .docx
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services.file_parser import FileParserService
from app.models import AnalysisRequest, AnalysisResponse, AnalysisOptions
from app.routes.analyze import analyze_impl
import json

router = APIRouter()

@router.post("/upload", response_model=AnalysisResponse)
async def upload_file(
    file: UploadFile = File(...),
    options: str = Form(default='{"mask": true, "blockHighRisk": false, "advancedDetection": true}')
):
    """
    Upload and analyze a file (.txt, .log, .pdf, .docx)

    This endpoint:
    1. Accepts binary file upload
    2. Parses/extracts text content
    3. Runs security analysis
    4. Returns analysis results
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )

        # Read file content
        content_bytes = await file.read()

        # Validate file size (max 10MB)
        try:
            FileParserService.validate_file_size(content_bytes, max_size_mb=10)
        except ValueError as e:
            raise HTTPException(
                status_code=413,
                detail=str(e)
            )

        # Parse file and extract text
        try:
            extracted_text, file_type = FileParserService.parse_file(
                file.filename,
                content_bytes
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"File parsing failed: {str(e)}"
            )

        # Parse options
        try:
            options_dict = json.loads(options)
            analysis_options = AnalysisOptions(**options_dict)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid options format: {str(e)}"
            )

        # Determine input type based on file type
        input_type_map = {
            "txt": "text",
            "log": "log",
            "pdf": "file",
            "docx": "file"
        }
        input_type = input_type_map.get(file_type.value, "text")

        # Create analysis request
        request = AnalysisRequest(
            inputType=input_type,
            content=extracted_text,
            options=analysis_options,
            filename=file.filename,
            content_type=file.content_type
        )

        # Run analysis
        result = await analyze_impl(request)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "File upload failed",
                "message": str(e),
                "code": "UPLOAD_FAILED"
            }
        )
