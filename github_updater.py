import os
import shutil
import subprocess
import tempfile
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext

# Git yolu
GIT_PATH = r"C:\Program Files\Git\cmd\git.exe"


class GitHubUpdaterApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Rezan Portfolio - GitHub Publisher")
    self.root.geometry("650x580")
    self.root.minsize(600, 550)

    self.create_widgets()

  def create_widgets(self):
    # --- 1. Klasör Seçim Alanı ---
    frame_folder = tk.LabelFrame(
        self.root, text=" Proje Klasörü ", font=("Arial", 10, "bold"), padx=10, pady=10
    )
    frame_folder.pack(fill="x", padx=15, pady=10)

    self.entry_path = tk.Entry(frame_folder, font=("Arial", 10), width=50)
    self.entry_path.insert(0, r"C:\Users\rezan\Desktop\Rezan-Portfolio")
    self.entry_path.pack(side="left", padx=(0, 10), expand=True, fill="x")

    btn_browse = tk.Button(
        frame_folder,
        text="Klasör Seç",
        command=self.browse_folder,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 9, "bold"),
    )
    btn_browse.pack(side="right")

    # --- 2. GitHub Ayarları ---
    frame_repo = tk.LabelFrame(
        self.root, text=" GitHub Depo (Repo) Ayarları ", font=("Arial", 10, "bold"), padx=10, pady=10
    )
    frame_repo.pack(fill="x", padx=15, pady=5)

    tk.Label(
        frame_repo,
        text="GitHub Repo Adı veya Tam URL (Örn: flag veya https://.../flag.git):",
        font=("Arial", 9),
    ).pack(anchor="w", pady=(0, 3))
    
    self.entry_repo_name = tk.Entry(frame_repo, font=("Arial", 11, "bold"))
    self.entry_repo_name.insert(0, "https://github.com/4rezan/rezan.github.io.git")
    self.entry_repo_name.pack(fill="x", pady=(0, 10))

    tk.Label(frame_repo, text="Commit Mesajı:", font=("Arial", 9)).pack(
        anchor="w", pady=(0, 3)
    )
    self.entry_msg = tk.Entry(frame_repo, font=("Arial", 10))
    self.entry_msg.insert(0, "Update Rezan portfolio")
    self.entry_msg.pack(fill="x")

    # --- 3. İşlem Başlatma Butonu ---
    self.btn_run = tk.Button(
        self.root,
        text="GitHub'a Yükle / Güncelle",
        command=self.start_git_process,
        bg="#2196F3",
        fg="white",
        font=("Arial", 11, "bold"),
        pady=8,
    )
    self.btn_run.pack(fill="x", padx=15, pady=15)

    # --- 4. Konsol Çıktısı (Canlı Log) ---
    frame_log = tk.LabelFrame(
        self.root, text=" İşlem Günlüğü (Console) ", font=("Arial", 10, "bold"), padx=10, pady=10
    )
    frame_log.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    self.log_text = scrolledtext.ScrolledText(
        frame_log, wrap=tk.WORD, font=("Consolas", 9), bg="#1e1e1e", fg="#00ff00"
    )
    self.log_text.pack(fill="both", expand=True)

  def browse_folder(self):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
      self.entry_path.delete(0, tk.END)
      self.entry_path.insert(0, folder_selected)

  def log(self, message):
    self.log_text.insert(tk.END, message + "\n")
    self.log_text.see(tk.END)

  def start_git_process(self):
    folder = self.entry_path.get().strip()
    repo_input = self.entry_repo_name.get().strip()
    commit_msg = self.entry_msg.get().strip()

    if not folder or not repo_input:
      messagebox.showerror("Hata", "Lütfen bir klasör seçin ve repo adını/linkini girin!")
      return

    self.btn_run.config(state=tk.DISABLED, bg="#9e9e9e")
    self.log_text.delete(1.0, tk.END)

    threading.Thread(
        target=self.run_automation,
        args=(folder, repo_input, commit_msg),
        daemon=True,
    ).start()

  def run_automation(self, folder, repo_input, commit_msg):
    git_cmd = GIT_PATH if os.path.exists(GIT_PATH) else shutil.which("git")
    if not git_cmd:
      self.log("[HATA] Git for Windows bulunamadı. Önce Git'i kurup tekrar deneyin.")
      messagebox.showerror("Git bulunamadı", "Git for Windows kurulu değil veya PATH'e ekli değil.")
      self.btn_run.config(state=tk.NORMAL, bg="#2196F3")
      return

    source_folder = os.path.abspath(folder)
    if repo_input.startswith("http://") or repo_input.startswith("https://"):
      repo_url = repo_input
    else:
      repo_url = f"https://github.com/4rezan/{repo_input}.git"

    try:
      self.log(f"Kaynak klasör: {source_folder}\nDepo: {repo_url}")
      self.log("[1/4] GitHub main dalı temiz geçici klasöre alınıyor...")
      with tempfile.TemporaryDirectory(prefix="zpass-github-upload-") as temp_root:
        clone_folder = os.path.join(temp_root, "repo")
        clone_res = subprocess.run(
            [git_cmd, "clone", "--branch", "main", "--single-branch", repo_url, clone_folder],
            capture_output=True, text=True, cwd=source_folder
        )
        if clone_res.returncode != 0:
          self.log(clone_res.stderr)
          messagebox.showerror("GitHub deposu açılamadı", "GitHub oturumunu ve main dalını kontrol edin. Ayrıntılar işlem günlüğünde.")
          return

        self.log("[2/4] Proje dosyaları, gizli anahtarlar ve derleme dosyaları atlanarak kopyalanıyor...")
        skipped_large = []
        ignored_names = shutil.ignore_patterns(
            ".git", ".firebase", "node_modules", "bin", "obj", "dist",
            ".env", ".env.*", "*firebase-adminsdk*.json", "*service-account*.json",
            "serviceAccountKey.json", "*.apk", "*.aab", "*.ipa", "*.exe", "*.dll",
            "*.msi", "*.jks", "*.keystore", "*.p12",
            "*.tmp.old", "artifacts/releases",
            "quarantined-third-party-page-copy-20261028"
        )
        def ignore_upload(path, names):
          ignored = set(ignored_names(path, names))
          for name in names:
            full_path = os.path.join(path, name)
            if os.path.isfile(full_path) and os.path.getsize(full_path) >= 90 * 1024 * 1024:
              ignored.add(name)
              skipped_large.append(os.path.relpath(full_path, source_folder))
          return ignored

        shutil.copytree(source_folder, clone_folder, dirs_exist_ok=True, ignore=ignore_upload)
        for skipped_path in skipped_large:
          self.log(f"[Atlandı: 90 MB üzeri] {skipped_path}")

        subprocess.run([git_cmd, "config", "user.name", "4rezan"], cwd=clone_folder, capture_output=True, text=True)
        subprocess.run([git_cmd, "config", "user.email", "4rezan@users.noreply.github.com"], cwd=clone_folder, capture_output=True, text=True)
        add_res = subprocess.run([git_cmd, "add", "-A"], cwd=clone_folder, capture_output=True, text=True)
        if add_res.returncode != 0:
          self.log(add_res.stderr)
          messagebox.showerror("Dosyalar eklenemedi", "Git dosyaları hazırlayamadı. Ayrıntılar işlem günlüğünde.")
          return

        status_res = subprocess.run([git_cmd, "status", "--porcelain"], cwd=clone_folder, capture_output=True, text=True)
        if not status_res.stdout.strip():
          self.log("Uzak depo zaten güncel; yeni commit oluşturulmadı.")
          messagebox.showinfo("Güncel", "GitHub deposunda değişiklik yok.")
          return

        self.log("[3/4] Tek commit hazırlanıyor...")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_res = subprocess.run(
            [git_cmd, "commit", "-m", f"{commit_msg} - {now}"],
            cwd=clone_folder, capture_output=True, text=True
        )
        if commit_res.returncode != 0:
          self.log(commit_res.stderr)
          messagebox.showerror("Commit başarısız", "Değişiklikler commit edilemedi. Ayrıntılar işlem günlüğünde.")
          return
        self.log(commit_res.stdout)

        self.log("[4/4] Temiz commit GitHub main dalına gönderiliyor...")
        push_res = subprocess.run([git_cmd, "push", "origin", "main"], cwd=clone_folder, capture_output=True, text=True)
        self.log(push_res.stdout)
        if push_res.returncode != 0:
          self.log(f"\n[HATA]: {push_res.stderr}")
          messagebox.showwarning("GitHub'a yükleme başarısız", "GitHub oturumu, depo yazma izni ve main dalı korumasını kontrol et. Ayrıntılar işlem günlüğünde.")
          return

      self.log("\nYükleme tamamlandı. Kaynak klasörünün Git geçmişi gönderilmedi.")
      messagebox.showinfo("Başarılı", "Proje dosyaları GitHub main dalına gönderildi. Cloudflare Pages Git bağlantısı açıksa dağıtım başlayacak.")

    except Exception as e:
      self.log(f"\n[KRİTİK HATA]: {e}")
      messagebox.showerror("Hata", f"Beklenmeyen bir hata oluştu:\n{e}")
    finally:
      self.btn_run.config(state=tk.NORMAL, bg="#2196F3")


if __name__ == "__main__":
  root = tk.Tk()
  app = GitHubUpdaterApp(root)
  root.mainloop()
