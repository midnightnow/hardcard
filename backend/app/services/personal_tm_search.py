#!/usr/bin/env python3
"""
🔍 Personal Time Machine Search Agent
Use HardCard's omniscient agent to find YOUR files in YOUR actual Time Machine backups
"""

import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class PersonalTMFinder:
    """Your personal intelligent Time Machine search agent"""
    
    def __init__(self, db_path: str = "personal_tm_search.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
    
    def _init_db(self):
        """Initialize personal search database"""
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS tm_files (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL,
            filename TEXT NOT NULL,
            size INTEGER,
            modified TEXT,
            backup_date TEXT,
            full_path TEXT,
            file_type TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_filename ON tm_files(filename);
        CREATE INDEX IF NOT EXISTS idx_path ON tm_files(path);
        CREATE INDEX IF NOT EXISTS idx_type ON tm_files(file_type);
        """)
        self.conn.commit()
    
    def find_time_machine_backups(self) -> List[str]:
        """Find your actual Time Machine backup locations"""
        backup_paths = []
        
        # Check common Time Machine locations
        possible_locations = [
            "/Volumes/*/Backups.backupdb",
            "/System/Volumes/Data/.timemachine",
        ]
        
        from glob import glob
        for pattern in possible_locations:
            paths = glob(pattern)
            backup_paths.extend(paths)
        
        # Also try tmutil
        try:
            import subprocess
            result = subprocess.run(
                ["tmutil", "destinationinfo"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if "Mount Point" in line:
                        mount_point = line.split(':')[1].strip()
                        backup_db = Path(mount_point) / "Backups.backupdb"
                        if backup_db.exists():
                            backup_paths.append(str(backup_db))
        except Exception:
            pass
        
        return list(set(backup_paths))
    
    def quick_index_recent_backup(self, backup_path: str, max_files: int = 10000):
        """Quickly index just the most recent backup for immediate searching"""
        backup_db = Path(backup_path)
        
        print(f"🔍 Quick-indexing recent backup from: {backup_db}")
        
        if not backup_db.exists():
            print(f"❌ Backup path doesn't exist: {backup_db}")
            return
        
        try:
            # Find the most recent backup
            machines = [d for d in backup_db.iterdir() if d.is_dir() and not d.name.startswith('.')]
            
            if not machines:
                print("❌ No machine backups found")
                return
            
            machine = machines[0]  # Use first machine
            snapshots = sorted([d for d in machine.iterdir() if d.is_dir() and not d.name.startswith('.')], reverse=True)
            
            if not snapshots:
                print("❌ No snapshots found")
                return
            
            latest_snapshot = snapshots[0]
            print(f"📸 Indexing latest snapshot: {latest_snapshot.name}")
            
            # Quick index of common user directories
            user_dirs = [
                "Users",  # All user data
                "Applications",  # Apps
            ]
            
            file_count = 0
            indexed_files = []
            
            for user_dir in user_dirs:
                user_path = latest_snapshot / user_dir
                if not user_path.exists():
                    continue
                
                print(f"📁 Indexing {user_dir}...")
                
                for root, dirs, files in os.walk(user_path):
                    if file_count >= max_files:
                        break
                    
                    # Skip certain directories for speed
                    dirs[:] = [d for d in dirs if d not in [
                        '.Trash', 'Cache', 'Caches', 'Logs', 'node_modules', '.git'
                    ]]
                    
                    for filename in files:
                        if file_count >= max_files:
                            break
                        
                        if filename.startswith('.'):
                            continue
                        
                        filepath = Path(root) / filename
                        try:
                            stat = filepath.stat()
                            
                            # Determine file type
                            ext = filepath.suffix.lower()
                            if ext in ['.jpg', '.png', '.gif', '.heic']:
                                file_type = 'image'
                            elif ext in ['.pdf', '.doc', '.docx', '.txt']:
                                file_type = 'document'
                            elif ext in ['.mp4', '.mov', '.avi']:
                                file_type = 'video'
                            elif ext in ['.py', '.js', '.swift', '.cpp']:
                                file_type = 'code'
                            else:
                                file_type = 'other'
                            
                            rel_path = str(filepath.relative_to(latest_snapshot))
                            
                            indexed_files.append((
                                rel_path,
                                filename,
                                stat.st_size,
                                datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                latest_snapshot.name,
                                str(filepath),
                                file_type
                            ))
                            
                            file_count += 1
                            
                            if file_count % 1000 == 0:
                                print(f"   Indexed {file_count:,} files...")
                                
                        except Exception:
                            continue
            
            # Insert into database
            if indexed_files:
                self.conn.executemany(
                    """INSERT OR REPLACE INTO tm_files 
                       (path, filename, size, modified, backup_date, full_path, file_type)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    indexed_files
                )
                self.conn.commit()
                
                print(f"✅ Indexed {len(indexed_files):,} files from your Time Machine backup!")
            else:
                print("❌ No files found to index")
                
        except PermissionError:
            print("🔒 Permission denied - need Full Disk Access to read Time Machine")
            print("💡 Go to System Settings > Privacy & Security > Full Disk Access")
            print("💡 Add Terminal or Python to the list")
        except Exception as e:
            print(f"❌ Error indexing backup: {e}")
    
    def search_your_files(self, query: str, file_type: str = None, limit: int = 20) -> List[Dict]:
        """Search YOUR actual Time Machine files"""
        sql = """
            SELECT filename, path, size, modified, backup_date, file_type, full_path
            FROM tm_files 
            WHERE (filename LIKE ? OR path LIKE ?)
        """
        
        params = [f"%{query}%", f"%{query}%"]
        
        if file_type:
            sql += " AND file_type = ?"
            params.append(file_type)
        
        sql += " ORDER BY size DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor]
    
    def find_large_files(self, min_size_mb: int = 100, limit: int = 20) -> List[Dict]:
        """Find your largest files"""
        min_size_bytes = min_size_mb * 1024 * 1024
        
        cursor = self.conn.execute(
            """SELECT filename, path, size, modified, backup_date, file_type
               FROM tm_files 
               WHERE size >= ?
               ORDER BY size DESC
               LIMIT ?""",
            (min_size_bytes, limit)
        )
        
        return [dict(row) for row in cursor]
    
    def find_by_extension(self, extension: str, limit: int = 20) -> List[Dict]:
        """Find files by extension"""
        cursor = self.conn.execute(
            """SELECT filename, path, size, modified, backup_date, file_type
               FROM tm_files 
               WHERE filename LIKE ?
               ORDER BY size DESC
               LIMIT ?""",
            (f"%.{extension}", limit)
        )
        
        return [dict(row) for row in cursor]
    
    def get_stats(self) -> Dict:
        """Get stats about your indexed files"""
        cursor = self.conn.execute(
            "SELECT COUNT(*) as total_files, SUM(size) as total_size FROM tm_files"
        )
        row = cursor.fetchone()
        
        cursor = self.conn.execute(
            "SELECT file_type, COUNT(*) as count FROM tm_files GROUP BY file_type ORDER BY count DESC"
        )
        file_types = {row['file_type']: row['count'] for row in cursor}
        
        return {
            'total_files': row['total_files'],
            'total_size_gb': (row['total_size'] or 0) / (1024**3),
            'file_types': file_types
        }

def main():
    """Interactive Time Machine search for your personal files"""
    print("🔍 HardCard Personal Time Machine Search Agent")
    print("===============================================")
    print("Find YOUR files in YOUR Time Machine backups instantly!\n")
    
    finder = PersonalTMFinder()
    
    # Check if already indexed
    stats = finder.get_stats()
    if stats['total_files'] > 0:
        print(f"📊 Already indexed: {stats['total_files']:,} files ({stats['total_size_gb']:.1f} GB)")
        print("File types:", stats['file_types'])
    else:
        print("🔍 Finding your Time Machine backups...")
        backup_paths = finder.find_time_machine_backups()
        
        if backup_paths:
            print(f"✅ Found backup locations:")
            for path in backup_paths:
                print(f"  - {path}")
            
            print("\n⚡ Quick-indexing most recent backup (this may take a moment)...")
            finder.quick_index_recent_backup(backup_paths[0])
            
            stats = finder.get_stats()
            if stats['total_files'] > 0:
                print(f"\n📊 Indexed: {stats['total_files']:,} files ({stats['total_size_gb']:.1f} GB)")
            else:
                print("\n❌ No files were indexed (likely permission issue)")
                return
        else:
            print("❌ No Time Machine backups found")
            return
    
    print("\n🎯 SEARCH EXAMPLES:")
    print("==================")
    
    # Example searches
    searches = [
        ("photo", "Find photos"),
        ("document", "Find documents"), 
        ("presentation", "Find presentations"),
        ("project", "Find project files")
    ]
    
    for query, description in searches:
        results = finder.search_your_files(query, limit=3)
        print(f"\n🔎 {description} ('{query}'):")
        if results:
            for i, file in enumerate(results[:3], 1):
                size_mb = file['size'] / (1024**2)
                print(f"  {i}. {file['filename']} ({size_mb:.1f} MB) - {file['backup_date']}")
        else:
            print("  No matches found")
    
    # Show largest files
    print("\n🐘 YOUR LARGEST FILES:")
    large_files = finder.find_large_files(min_size_mb=50, limit=5)
    for i, file in enumerate(large_files, 1):
        size_mb = file['size'] / (1024**2)
        print(f"  {i}. {file['filename']} ({size_mb:.0f} MB) - {file['file_type']}")
    
    print("\n✨ INTERACTIVE SEARCH:")
    print("=====================")
    print("Now you can search for anything in your Time Machine backups!")
    print("Examples:")
    print("  finder.search_your_files('vacation')  # Find vacation files")
    print("  finder.search_your_files('2023')      # Find 2023 files")
    print("  finder.find_by_extension('pdf')       # Find all PDFs")
    print("  finder.find_large_files(500)          # Files >500MB")
    
    return finder

if __name__ == "__main__":
    finder = main()
