import os
import json
from pathlib import Path
from typing import List, Dict

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Static, DataTable, Footer, Input, Button
from textual.screen import ModalScreen
from textual import work
from dotenv import load_dotenv, set_key

from .scanner import scan_drive
from .ai_engine import run_ai_analysis
from .utils import human_size

# Aesthetics inspired by BrainKernel
CSS = """
Screen { background: #0a0a0a; }

# log_panel { width: 45%; background: #0f111a; border: solid #00ffff; }
.ttl { color: #00ffff; text-style: bold; padding: 1; text-align: center; background: #1a1a1a; }

# dr { height: 100%; align: center middle; }
.d { width: 1fr; height: 4; content-align: center middle; }
Footer { background: #1a1a1a; }
Footer > .footer--key { color: #00ffff; background: #0a0a0a; }

KeyScreen { align: center middle; }
# box { padding: 1 2; border: solid #00ffff; background: #111; width: 50; height: 12; }
# btns { height: 3; align: center middle; margin-top: 1; }
Button { margin: 0 1; min-width: 10; }

ConfirmScreen { align: center middle; }
# confirm-box { padding: 1 2; border: solid #ff0000; background: #111; width: 50; height: 12; }
# confirm-title { color: #ff0000; text-style: bold; text-align: center; }
# confirm-msg { text-align: center; margin-top: 1; }
"""

LOGO = """[#00ffff]╔═╗╦  ╔╦╗╦═╗╦╦  ╦╔═╗  ╔═╗╦  ╔═╗╔═╗╔╗╔╔═╗╦═╗
╠═╣║   ║║╠╦╝║╚╗╔╝║╣   ║  ║  ║╣ ╠═╣║║║║╣ ╠╦╝
╩ ╩╩═╝═╩╝╩╚═╩ ╚╝ ╚═╝  ╚═╝╩═╝╚═╝╩ ╩╝╚╝╚═╝╩╚═[/]"""

ENV_FILE = ".env"

class KeyScreen(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Close"), ("enter", "save_key", "Save")]

    def compose(self) -> ComposeResult:
        yield Container(
            Static("API KEY REQUIRED", id="t", classes="ttl"),
            Static("Please enter your Groq API Key:", id="s"),
            Input(placeholder="gsk_...", id="i"),
            Horizontal(Button("Save", id="save"), Button("Cancel", id="cancel"), id="btns"),
            id="box"
        )

    def on_button_pressed(self, e):
        if e.button.id == "save":
            self.do_save()
        else:
            self.dismiss(False)

    def action_save_key(self):
        self.do_save()

    def do_save(self):
        k = self.query_one("#i", Input).value.strip()
        if k:
            if not os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'w') as f: pass
            set_key(ENV_FILE, "GROQ_API_KEY", k)
            self.dismiss(k)

class ConfirmScreen(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Close"), ("y", "yes", "Yes"), ("n", "no", "No")]

    def __init__(self, message: str):
        super().__init__()
        self.msg = message

    def compose(self) -> ComposeResult:
        yield Container(
            Static("CONFIRM DELETION", id="confirm-title"),
            Static(self.msg, id="confirm-msg"),
            Horizontal(Button("Yes (Y)", id="yes", variant="error"), Button("No (N)", id="no"), id="btns"),
            id="confirm-box"
        )

    def on_button_pressed(self, e):
        self.dismiss(e.button.id == "yes")

    def action_yes(self):
        self.dismiss(True)

    def action_no(self):
        self.dismiss(False)

class AIDriveCleanerApp(App):
    CSS = CSS
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("k", "key", "API Key"),
        ("s", "scan", "Scan Drive"),
        ("d", "delete", "Delete Junk")
    ]

    def __init__(self):
        super().__init__()
        self.api_key = None
        self.logs = []
        self.files_to_analyze = []
        self.safe_delete_files = []
        self.total_size = 0
        self.scanning = False
        
    def compose(self) -> ComposeResult:
        yield Container(
            Static(LOGO, id="logo"),
            Static("Ready", id="status", classes="ttl"),
            id="hdr"
        )
        yield Horizontal(
            Container(Static("FILES FOUND", classes="ttl"), DataTable(id="tbl"), id="procs"),
            Container(Static("AI BRAIN STREAM", classes="ttl"), ScrollableContainer(id="scroll"), id="log_panel"),
            id="main"
        )
        yield Footer()

    def on_mount(self):
        t = self.query_one("#tbl", DataTable)
        t.add_columns("PATH", "SIZE", "VERDICT", "REASON")
        t.cursor_type = "row"
        
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            self.log_msg("[#ffff00]> No API Key found. Press 'k' to enter one.[/]")
            self.action_key()
        else:
            self.log_msg("[#00ff00]> API Key loaded. Press 's' to start scanning.[/]")

    def log_msg(self, msg: str):
        self.logs.insert(0, msg)
        del self.logs[50:]  # Keep last 50 logs
        try:
            sc = self.query_one("#scroll", ScrollableContainer)
            sc.remove_children()
            for line in self.logs:
                sc.mount(Static(line))
        except Exception:
            pass

    def action_key(self):
        def save_callback(k):
            if k:
                self.api_key = k
                self.log_msg("[#00ff00]> API Key saved successfully![/]")
        self.push_screen(KeyScreen(), save_callback)

    def action_scan(self):
        if not self.api_key:
            self.log_msg("[#ff0000]> Error: Enter API Key first (Press 'k')[/]")
            return
            
        if self.scanning:
            return
            
        self.scanning = True
        self.files_to_analyze = []
        self.safe_delete_files = []
        self.total_size = 0
        
        t = self.query_one("#tbl", DataTable)
        t.clear()
        
        self.query_one("#status", Static).update("Scanning C: drive...")
        self.log_msg("[#00ffff]> Starting deep scan of C: drive...[/]")
        self.run_scan_worker()

    @work(thread=True)
    def run_scan_worker(self):
        for file_info in scan_drive(start_path="C:\\", max_depth=5):
            self.files_to_analyze.append(file_info)
            self.total_size += file_info['size']
            
            # Update UI from thread
            self.call_from_thread(self.add_scanned_file, file_info)
            
        self.call_from_thread(self.finish_scan)

    def add_scanned_file(self, file_info: dict):
        t = self.query_one("#tbl", DataTable)
        t.add_row(
            file_info['path'], 
            human_size(file_info['size']), 
            "PENDING", 
            "",
            key=file_info['path']
        )
        self.query_one("#status", Static).update(f"Found {len(self.files_to_analyze)} files...")

    def finish_scan(self):
        self.log_msg(f"[#00ff00]> Scan complete! Found {len(self.files_to_analyze)} files ({human_size(self.total_size)})[/]")
        
        if not self.files_to_analyze:
            self.query_one("#status", Static).update("Drive is clean!")
            self.scanning = False
            return
            
        self.query_one("#status", Static).update("AI is analyzing files...")
        self.log_msg("[#00ffff]> Dispatching files to Groq AI...[/]")
        self.run_ai_worker()

    @work(thread=True)
    def run_ai_worker(self):
        try:
            for batch_results, model in run_ai_analysis(self.api_key, self.files_to_analyze):
                for res in batch_results:
                    if "error" in res:
                        self.call_from_thread(self.log_msg, f"[#ff0000]> {res['error']}[/]")
                        continue
                        
                    self.call_from_thread(self.update_file_verdict, res, model)
                    
            self.call_from_thread(self.finish_ai_analysis)
        except Exception as e:
            self.call_from_thread(self.log_msg, f"[#ff0000]> AI Analysis aborted: {e}[/]")
            self.call_from_thread(self.query_one("#status", Static).update, "AI Error")
            self.scanning = False

    def update_file_verdict(self, res: dict, model: str):
        path = res.get('path', '')
        verdict = res.get('verdict', 'KEEP')
        reason = res.get('reason', '')
        
        t = self.query_one("#tbl", DataTable)
        try:
            # Color code verdict
            if verdict == "SAFE_DELETE":
                v_text = f"[#ff0000]{verdict}[/]"
                
                # Find original file info to add to safe_delete list
                for f in self.files_to_analyze:
                    if f['path'] == path:
                        self.safe_delete_files.append(f)
                        break
                        
            elif verdict == "REVIEW":
                v_text = f"[#ffff00]{verdict}[/]"
            else:
                v_text = f"[#00ff00]{verdict}[/]"
                
            t.update_cell(path, "VERDICT", v_text)
            t.update_cell(path, "REASON", reason)
            
            # Add roast/reason to Brain Stream
            self.log_msg(f"[#888888][{model}][/] [#00ffff]{os.path.basename(path)}[/] -> {v_text}: {reason}")
            
        except Exception:
            pass

    def finish_ai_analysis(self):
        self.scanning = False
        reclaimable = sum(f['size'] for f in self.safe_delete_files)
        
        self.query_one("#status", Static).update(f"Ready. Reclaimable: {human_size(reclaimable)}")
        self.log_msg(f"[#00ff00]> Analysis complete. {len(self.safe_delete_files)} files safe to delete.[/]")
        self.log_msg("[#ffff00]> Press 'd' to delete SAFE_DELETE files.[/]")

    def action_delete(self):
        if not self.safe_delete_files:
            self.log_msg("[#ff0000]> No files marked as SAFE_DELETE.[/]")
            return
            
        reclaimable = sum(f['size'] for f in self.safe_delete_files)
        msg = f"Permanently delete {len(self.safe_delete_files)} files totaling {human_size(reclaimable)}?"
        
        def confirm_callback(confirmed: bool):
            if confirmed:
                self.execute_deletion()
            else:
                self.log_msg("[#ffff00]> Deletion cancelled.[/]")
                
        self.push_screen(ConfirmScreen(msg), confirm_callback)

    def execute_deletion(self):
        deleted_count = 0
        freed = 0
        t = self.query_one("#tbl", DataTable)
        
        for f in self.safe_delete_files:
            path = f['path']
            try:
                os.remove(path)
                deleted_count += 1
                freed += f['size']
                self.log_msg(f"[#00ff00]> Deleted:[/] {path}")
                # Remove from table
                try:
                    # Textual Datatable doesn't easily let us delete by key, so we just mark it
                    t.update_cell(path, "VERDICT", "[#444444]DELETED[/]")
                except:
                    pass
            except Exception as e:
                self.log_msg(f"[#ff0000]> Failed to delete:[/] {path} ({e})")
                
        self.safe_delete_files = [] # Clear the list
        self.log_msg(f"[#00ff00]>> DELETION COMPLETE. Freed {human_size(freed)} over {deleted_count} files.[/]")
        self.query_one("#status", Static).update(f"Freed {human_size(freed)}")

def run_app():
    app = AIDriveCleanerApp()
    app.run()
