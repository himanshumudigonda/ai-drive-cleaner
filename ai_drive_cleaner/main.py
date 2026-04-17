import os
import sys
import getpass
from dotenv import load_dotenv, set_key
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .scanner import scan_drive
from .ai_engine import run_ai_analysis
from .display import show_banner, show_summary, create_results_table, render_verdict, display_table, show_total_reclaimable
from .utils import human_size

console = Console()

def check_os():
    if os.name != 'nt':
        console.print("[bold red]Error: This tool is designed to run on Windows only.[/bold red]")
        sys.exit(1)

def get_api_key() -> str:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return api_key
        
    console.print("[yellow]Groq API key not found in environment.[/yellow]")
    api_key = getpass.getpass("Enter your Groq API key: ").strip()
    
    save = console.input("Save this key to .env for future runs? (y/N): ").strip().lower()
    if save == 'y':
        env_path = ".env"
        if not os.path.exists(env_path):
            with open(env_path, 'w') as f:
                pass
        set_key(env_path, "GROQ_API_KEY", api_key)
        console.print("[green]API key saved to .env[/green]")
        
    return api_key

def main():
    check_os()
    api_key = get_api_key()
    
    console.print("\n[bold cyan]AI Drive Cleaner[/bold cyan] is starting...")
    
    files_to_analyze = []
    total_size = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        scan_task = progress.add_task("[green]Scanning C: drive...", total=None)
        
        for file_info in scan_drive(start_path="C:\\", max_depth=5):
            files_to_analyze.append(file_info)
            total_size += file_info['size']
            progress.update(scan_task, description=f"[green]Scanning... found {len(files_to_analyze)} junk candidates")
            
    show_summary(len(files_to_analyze), human_size(total_size))
    
    if not files_to_analyze:
        console.print("[green]No junk candidates found. Your drive is clean![/green]")
        sys.exit(0)
        
    console.print("[cyan]Sending files to Groq AI for analysis...[/cyan]")
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            ai_task = progress.add_task("[cyan]AI Analyzing...", total=None)
            ai_results, active_model = run_ai_analysis(api_key, files_to_analyze)
    except Exception as e:
        console.print(f"[bold red]AI Analysis failed: {e}[/bold red]")
        sys.exit(1)
        
    os.system('cls' if os.name == 'nt' else 'clear')
    show_banner(active_model)
    
    table = create_results_table()
    
    safe_delete_files = []
    review_files = []
    total_reclaimable_size = 0
    
    results_map = {res.get('path'): res for res in ai_results}
    
    row_idx = 1
    for file_info in files_to_analyze:
        path = file_info['path']
        res = results_map.get(path)
        if not res:
            continue
            
        verdict = res.get('verdict', 'KEEP')
        reason = res.get('reason', '')
        size_str = human_size(file_info['size'])
        
        if verdict == "SAFE_DELETE":
            safe_delete_files.append(file_info)
            total_reclaimable_size += file_info['size']
        elif verdict == "REVIEW":
            review_files.append(file_info)
            total_reclaimable_size += file_info['size']
            
        table.add_row(
            str(row_idx),
            render_verdict(verdict),
            size_str,
            file_info['modified_date'],
            path,
            reason
        )
        row_idx += 1
        
    display_table(table)
    show_total_reclaimable(human_size(total_reclaimable_size))
    
    to_delete = []
    
    if safe_delete_files:
        ans = console.input(f"Delete {len(safe_delete_files)} SAFE_DELETE files? (y/N): ").strip().lower()
        if ans == 'y':
            to_delete.extend(safe_delete_files)
            
            if review_files:
                ans_review = console.input(f"Also delete {len(review_files)} REVIEW files? (y/N): ").strip().lower()
                if ans_review == 'y':
                    to_delete.extend(review_files)
    elif review_files:
        ans_review = console.input(f"Delete {len(review_files)} REVIEW files? (y/N): ").strip().lower()
        if ans_review == 'y':
            to_delete.extend(review_files)
            
    if not to_delete:
        console.print("[green]No files were deleted. Exiting.[/green]")
        sys.exit(0)
        
    total_del_size = sum(f['size'] for f in to_delete)
    final_confirm = console.input(f"\n[bold red]Permanently delete {len(to_delete)} files totaling {human_size(total_del_size)}? Type YES to confirm: [/bold red]")
    
    if final_confirm != "YES":
        console.print("[yellow]Deletion cancelled. No files were deleted.[/yellow]")
        sys.exit(0)
        
    console.print("\n[bold]Deleting files...[/bold]")
    deleted_count = 0
    freed_space = 0
    failed_count = 0
    
    for f in to_delete:
        path = f['path']
        try:
            os.remove(path)
            console.print(f"[green]✓[/green] Deleted: {path}")
            deleted_count += 1
            freed_space += f['size']
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to delete {path}: {e}")
            failed_count += 1
            
    console.print("\n[bold cyan]Final Summary:[/bold cyan]")
    console.print(f"Files deleted: {deleted_count}")
    console.print(f"Space freed: {human_size(freed_space)}")
    if failed_count > 0:
        console.print(f"[red]Failed to delete: {failed_count} files[/red]")

if __name__ == "__main__":
    main()
