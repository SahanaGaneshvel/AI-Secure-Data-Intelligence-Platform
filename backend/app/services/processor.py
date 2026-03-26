"""
Enhanced processing engine for large file handling
Provides: chunking, streaming, progress tracking
"""
from typing import List, Dict, AsyncGenerator
import asyncio
from app.models import Finding

class ProcessingEngine:
    """
    Handles large file processing with chunking and streaming capabilities
    """

    # Configuration
    MAX_CHUNK_SIZE = 50000  # 50KB per chunk
    MAX_LINES_PER_CHUNK = 1000

    @staticmethod
    def chunk_content(content: str, max_lines: int = MAX_LINES_PER_CHUNK) -> List[Dict]:
        """
        Split large content into manageable chunks
        Returns list of chunks with metadata
        """
        lines = content.split('\n')
        total_lines = len(lines)
        chunks = []

        for i in range(0, total_lines, max_lines):
            chunk_lines = lines[i:i + max_lines]
            chunks.append({
                'chunk_id': len(chunks),
                'start_line': i + 1,
                'end_line': min(i + max_lines, total_lines),
                'content': '\n'.join(chunk_lines),
                'line_count': len(chunk_lines)
            })

        return chunks

    @staticmethod
    async def process_chunks_async(chunks: List[Dict], detector_func) -> List[Finding]:
        """
        Process chunks asynchronously for better performance
        """
        async def process_chunk(chunk):
            # Simulate async processing
            await asyncio.sleep(0.01)  # Small delay to allow other tasks
            detections = detector_func(chunk['content'])

            # Adjust line numbers based on chunk offset
            offset = chunk['start_line'] - 1
            for detection in detections:
                if detection.get('line'):
                    detection['line'] += offset

            return detections

        # Process all chunks concurrently
        tasks = [process_chunk(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks)

        # Flatten results
        all_detections = []
        for chunk_detections in results:
            all_detections.extend(chunk_detections)

        return all_detections

    @staticmethod
    async def stream_progress(total_chunks: int) -> AsyncGenerator[Dict, None]:
        """
        Stream processing progress updates
        Use with WebSocket or Server-Sent Events
        """
        for i in range(total_chunks):
            await asyncio.sleep(0.1)  # Simulate processing time
            progress = {
                'chunk': i + 1,
                'total': total_chunks,
                'percentage': int(((i + 1) / total_chunks) * 100),
                'status': 'processing'
            }
            yield progress

        # Final completion message
        yield {
            'chunk': total_chunks,
            'total': total_chunks,
            'percentage': 100,
            'status': 'completed'
        }

    @staticmethod
    def should_chunk(content: str) -> bool:
        """
        Determine if content should be chunked based on size
        """
        line_count = len(content.split('\n'))
        byte_size = len(content.encode('utf-8'))

        return (line_count > ProcessingEngine.MAX_LINES_PER_CHUNK or
                byte_size > ProcessingEngine.MAX_CHUNK_SIZE)

    @staticmethod
    def merge_detections(chunk_results: List[List[Dict]]) -> List[Dict]:
        """
        Merge detection results from multiple chunks
        Handles deduplication and line number adjustment
        """
        seen = set()
        merged = []

        for chunk_detections in chunk_results:
            for detection in chunk_detections:
                # Create unique key for deduplication
                key = (detection.get('line'), detection.get('type'), detection.get('matched_text'))

                if key not in seen:
                    seen.add(key)
                    merged.append(detection)

        # Sort by line number
        merged.sort(key=lambda x: x.get('line', 0))

        return merged

    @staticmethod
    async def process_large_file(content: str, detector_func, progress_callback=None):
        """
        Main entry point for processing large files
        Automatically chunks if needed, processes async, returns results
        """
        if not ProcessingEngine.should_chunk(content):
            # Small file, process directly
            if progress_callback:
                await progress_callback({'percentage': 100, 'status': 'completed'})
            return detector_func(content)

        # Large file, use chunking
        chunks = ProcessingEngine.chunk_content(content)
        total_chunks = len(chunks)

        if progress_callback:
            await progress_callback({
                'percentage': 0,
                'status': 'started',
                'total_chunks': total_chunks
            })

        # Process chunks with progress updates
        all_detections = []
        for i, chunk in enumerate(chunks):
            detections = detector_func(chunk['content'])

            # Adjust line numbers
            offset = chunk['start_line'] - 1
            for detection in detections:
                if detection.get('line'):
                    detection['line'] += offset

            all_detections.extend(detections)

            # Update progress
            if progress_callback:
                await progress_callback({
                    'percentage': int(((i + 1) / total_chunks) * 100),
                    'status': 'processing',
                    'chunk': i + 1,
                    'total_chunks': total_chunks
                })

        return all_detections
