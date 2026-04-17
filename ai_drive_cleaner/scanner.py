import os
import datetime

TARGET_EXTENSIONS = {'.tmp', '.temp', '.log', '.bak', '.old', '.dmp', '.chk', '.cache', '.crdownload', '.part'}
TARGET_FOLDERS = {'temp', 'cache', 'prefetch', 'recent', 'crash reports', 'thumbnails', '$recycle.bin'}
SKIP_FOLDERS = {'windows', 'program files', 'program files (x86)', 'programdata', 'system volume information'}

def is_target_file(file_path: str, filename: str) -> bool:
    """Determine if a file matches the target criteria."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in TARGET_EXTENSIONS:
        return True
    
    # Check if file is in a target folder
    parts = file_path.lower().split(os.sep)
    for folder in TARGET_FOLDERS:
        if folder in parts:
            return True
            
    return False

def scan_drive(start_path: str = "C:\\", max_depth: int = 5):
    """
    Recursively scan the drive up to max_depth.
    Yields dict with: path, size, modified_date, ext, folder
    """
    start_depth = start_path.count(os.sep)
    
    for root, dirs, files in os.walk(start_path):
        current_depth = root.count(os.sep) - start_depth
        
        if current_depth >= max_depth:
            # Prevent going deeper by clearing dirs
            dirs[:] = []
            continue

        # Filter out skipped directories
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_FOLDERS]

        for file in files:
            file_path = os.path.join(root, file)
            
            if is_target_file(file_path, file):
                try:
                    stat = os.stat(file_path)
                    size = stat.st_size
                    mtime = stat.st_mtime
                    modified_date = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                    ext = os.path.splitext(file)[1].lower()
                    folder = os.path.basename(root)
                    
                    yield {
                        "path": file_path,
                        "size": size,
                        "modified_date": modified_date,
                        "ext": ext,
                        "folder": folder
                    }
                except (OSError, PermissionError):
                    # Skip files we can't access
                    continue
