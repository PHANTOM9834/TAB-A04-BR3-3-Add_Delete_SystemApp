import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import tempfile

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class RomPatcherApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("Android System Image Patcher")
    self.geometry("620x640")

    # --- 共通の system.img 選択部分 ---
    self.label_img = ctk.CTkLabel(self, text="system.imgのパス:")
    self.label_img.pack(pady=(15, 5), padx=30)

    self.frame_img = ctk.CTkFrame(self, fg_color="transparent")
    self.frame_img.pack(padx=30)

    self.entry_img = ctk.CTkEntry(self.frame_img, width=420)
    self.entry_img.pack(side="left", padx=(0, 10))

    self.btn_browse_img = ctk.CTkButton(
        self.frame_img, text="参照...", width=70, command=self.select_img
    )
    self.btn_browse_img.pack(side="left")

    # --- 上部タブビューの作成 (アプリ追加 / アプリ削除) ---
    self.tabview = ctk.CTkTabview(self, width=560, height=310)
    self.tabview.pack(padx=30, pady=15)

    self.tab_add = self.tabview.add("アプリ追加")
    self.tab_remove = self.tabview.add("アプリ削除")

    # ==================== 「アプリ追加」タブの中身 ====================
    self.label_app = ctk.CTkLabel(
        self.tab_add, text="追加するアプリフォルダのパス:"
    )
    self.label_app.pack(pady=(10, 5))

    self.frame_add_input = ctk.CTkFrame(self.tab_add, fg_color="transparent")
    self.frame_add_input.pack(pady=5)

    self.entry_app = ctk.CTkEntry(self.frame_add_input, width=400)
    self.entry_app.pack(side="left", padx=(0, 10))

    self.btn_browse_app = ctk.CTkButton(
        self.frame_add_input, text="参照...", width=70, command=self.select_app_dir
    )
    self.btn_browse_app.pack(side="left")

    self.label_dest = ctk.CTkLabel(self.tab_add, text="配置先ディレクトリ:")
    self.label_dest.pack(pady=(10, 5))

    self.dest_var = ctk.StringVar(value="priv-app")
    self.segment_dest = ctk.CTkSegmentedButton(
        self.tab_add, values=["priv-app", "app"], variable=self.dest_var, width=400
    )
    self.segment_dest.pack(pady=5)

    self.btn_run_add = ctk.CTkButton(
        self.tab_add,
        text="追加パッチを適用して再パック",
        fg_color="green",
        hover_color="darkgreen",
        command=self.run_add_patch,
    )
    self.btn_run_add.pack(pady=15)

    # ==================== 「アプリ削除」タブの中身 ====================
    self.label_rem_dest = ctk.CTkLabel(
        self.tab_remove, text="検索・削除対象ディレクトリ:"
    )
    self.label_rem_dest.pack(pady=(10, 5))

    self.rem_dest_var = ctk.StringVar(value="priv-app")
    self.segment_rem_dest = ctk.CTkSegmentedButton(
        self.tab_remove,
        values=["priv-app", "app"],
        variable=self.rem_dest_var,
        command=self.on_rem_dest_changed,  # 切り替え時のイベント関数
        width=400,
    )
    self.segment_rem_dest.pack(pady=5)

    # 一覧取得ボタンとプルダウンを配置するフレーム
    self.frame_rem_select = ctk.CTkFrame(self.tab_remove, fg_color="transparent")
    self.frame_rem_select.pack(pady=10)

    self.btn_fetch_list = ctk.CTkButton(
        self.frame_rem_select,
        text="一覧を取得",
        width=100,
        command=self.fetch_app_list,
    )
    self.btn_fetch_list.pack(side="left", padx=(0, 10))

    # アプリ選択用のプルダウン
    self.app_list_var = ctk.StringVar(value="（先に一覧を取得してください）")
    self.option_apps = ctk.CTkOptionMenu(
        self.frame_rem_select,
        values=["（先に一覧を取得してください）"],
        variable=self.app_list_var,
        width=290,
    )
    self.option_apps.pack(side="left")

    self.btn_run_rem = ctk.CTkButton(
        self.tab_remove,
        text="選択したアプリを削除して再パック",
        fg_color="darkred",
        hover_color="firebrick",
        command=self.run_remove_patch,
    )
    self.btn_run_rem.pack(pady=15)

    # --- 共通のログ表示部分 ---
    self.text_log = ctk.CTkTextbox(self, width=560, height=110)
    self.text_log.pack(padx=30, pady=(0, 15))

    # --- 警告・免責事項のスペース ---
    warning_text = (
        "【重要なお知らせと免責事項 このツールを使用した場合下記に同意したことになります。】\n"
        "1. 本ツールはAndroidシステムのパーティション書き換えを行う高度なツールです。\n"
        "2. 誤った操作や不具合により、デバイスが起動しなくなる等のリスクがあります。\n"
        "3. 本ツールの使用によるいかなるデータの損失、機器の破損についても、\n"
        "   作者は一切の責任を負いません。自己責任でご利用ください。 \n"
        "4.本ツールを使用するにあたって絶対に以下のことは守ってください。 \n" \
        "   adb fastboot MTKClientのすべてのツールが必ず使用できること。 \n"
        "   特にMTKClientの場合依存関係が複雑かつAndroidの深い場所を扱うためfastbootが失敗したときに使えないと文鎮化します。 \n" 
        "   重要なパーティション、できればすべてのパーティションのバックアップをとっておくこと。 \n"
        "   パソコンとAndroidについてある程度の知識があること。"
        "5.今回作者が使用した環境はPython 3.12 ZorinOS18.1です。 \n"
        "   これはUbuntuベース向けに作られておりLinux系でも動作しないOSも存在しています。 \n"
        "   LinuxMintではsudoを使用してもマウントが読み込み専用であったためZorinOSであることを強く推奨します。"
    )

    self.text_warning = ctk.CTkTextbox(
        self, width=560, height=110, text_color="red"
    )
    self.text_warning.pack(padx=30, pady=(0, 15))

    self.text_warning.insert("0.0", warning_text)
    self.text_warning.configure(state="disabled")

  def select_img(self):
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.img"), ("All Files", "*.*")]
    )
    if file_path:
      self.entry_img.delete(0, tk.END)
      self.entry_img.insert(0, file_path)

  def select_app_dir(self):
    dir_path = filedialog.askdirectory()
    if dir_path:
      self.entry_app.delete(0, tk.END)
      self.entry_app.insert(0, dir_path)

  def log(self, message):
    self.text_log.insert(tk.END, message + "\n")
    self.text_log.see(tk.END)

  def mount_image(self, img_path, mount_point):
    """共通のマウント処理"""
    self.log(f"マウント先を作成中: {mount_point}")
    subprocess.run(["sudo", "mkdir", "-p", mount_point], check=True)

    self.log("system.imgをマウント中...")
    subprocess.run(
        ["sudo", "mount", "-o", "loop,rw", img_path, mount_point], check=True
    )

    mount_check = subprocess.run(
        ["findmnt", "-n", "-o", "OPTIONS", mount_point],
        capture_output=True,
        text=True,
    )
    if "ro" in mount_check.stdout:
      raise Exception("エラー: system.imgが読み込み専用 (ro) でマウントされました！")

  def on_rem_dest_changed(self, selected_value):
    """priv-app と app の切り替えボタンが押されたときに自動で一覧を再取得する"""
    # すでに system.img が選択されている場合のみ自動取得を試みる
    img_path = self.entry_img.get()
    if img_path and os.path.exists(img_path):
      self.fetch_app_list()
    else:
      # イメージ未選択ならプレースホルダーに戻す
      self.option_apps.configure(values=["（先に一覧を取得してください）"])
      self.app_list_var.set("（先に一覧を取得してください）")

  def fetch_app_list(self):
    """イメージを一時マウントして、選択されたディレクトリ内のフォルダ一覧を取得する"""
    img_path = self.entry_img.get()
    selected_dest = self.rem_dest_var.get()

    if not img_path:
      messagebox.showerror("エラー", "先にsystem.imgを選択してください。")
      return

    mount_point = tempfile.mkdtemp(prefix="android_sys_")
    self.log(f"=== [{selected_dest}] のアプリ一覧を取得中 ===")

    try:
      # 一時マウント
      self.mount_image(img_path, mount_point)

      target_dir = f"{mount_point}/{selected_dest}"

      if not os.path.exists(target_dir):
        self.log(f"警告: ディレクトリが存在しません: {target_dir}")
        self.option_apps.configure(values=["（アプリが見つかりません）"])
        self.app_list_var.set("（アプリが見つかりません）")
        return

      # フォルダ内のアイテムを取得
      items = os.listdir(target_dir)
      folders = [
          item
          for item in items
          if os.path.isdir(os.path.join(target_dir, item))
      ]

      if folders:
        folders.sort()
        self.option_apps.configure(values=folders)
        self.app_list_var.set(folders[0])
        self.log(f"取得成功: {len(folders)}個のアプリが見つかりました。")
      else:
        self.option_apps.configure(values=["（アプリなし）"])
        self.app_list_var.set("（アプリなし）")
        self.log("対象ディレクトリにフォルダが見つかりませんでした。")

    except Exception as e:
      self.log(f"[エラー発生]: {e}")
      messagebox.showerror("エラー", f"一覧の取得に失敗しました:\n{e}")

    finally:
      # アンマウント
      try:
        subprocess.run(["sudo", "umount", mount_point], check=True)
      except Exception:
        pass

  def run_add_patch(self):
    """アプリ追加処理"""
    img_path = self.entry_img.get()
    app_dir = self.entry_app.get()
    selected_dest = self.dest_var.get()

    if not img_path:
      messagebox.showerror("エラー", "system.imgを選択してください。")
      return
    if not app_dir:
      messagebox.showerror("エラー", "追加するアプリのフォルダを選択してください。")
      return

    mount_point = "/home/pc/sys"
    self.log("=== [追加処理] 開始 ===")

    try:
      self.mount_image(img_path, mount_point)

      target_base = f"{mount_point}/{selected_dest}"
      subprocess.run(["sudo", "mkdir", "-p", target_base], check=True)

      self.log(f"アプリをコピー中: {app_dir} -> {target_base}")
      subprocess.run(["sudo", "cp", "-r", app_dir, target_base], check=True)

      folder_name = os.path.basename(os.path.normpath(app_dir))
      target_path = f"{target_base}/{folder_name}"

      self.log(f"権限およびSELinux設定を適用中: {target_path}")
      subprocess.run(["sudo", "chown", "-R", "0:0", target_path], check=True)
      subprocess.run(
          [
              "sudo",
              "find",
              target_path,
              "-type",
              "d",
              "-exec",
              "chmod",
              "755",
              "{}",
              "+",
          ],
          check=True,
      )
      subprocess.run(
          [
              "sudo",
              "find",
              target_path,
              "-type",
              "f",
              "-exec",
              "chmod",
              "644",
              "{}",
              "+",
          ],
          check=True,
      )
      subprocess.run(
          ["sudo", "chcon", "-R", "u:object_r:system_file:s0", target_path],
          check=True,
      )

      # 変更をディスクに同期
      subprocess.run(["sudo", "sync"], check=True)

      self.log("アプリの追加が正常に完了しました！")
      messagebox.showinfo("成功", "アプリの追加と設定が完了しました。")

    except Exception as e:
      self.log(f"[エラー発生]: {e}")
      messagebox.showerror("エラー", f"処理に失敗しました:\n{e}")

    finally:
      self.log("アンマウント処理を実行中...")
      try:
        subprocess.run(["sudo", "umount", mount_point], check=True)
        self.log("アンマウント完了。")
      except Exception as ex:
        self.log(f"アンマウント時のエラー: {ex}")

  def run_remove_patch(self):
    """アプリ削除処理"""
    img_path = self.entry_img.get()
    app_name = self.app_list_var.get()
    selected_dest = self.rem_dest_var.get()

    if not img_path:
      messagebox.showerror("エラー", "system.imgを選択してください。")
      return
    if (
        not app_name
        or app_name.startswith("（")
        or app_name.endswith("）")
    ):
      messagebox.showerror(
          "エラー",
          "削除するアプリが正しく選択されていません。「一覧を取得」を押して選択してください。",
      )
      return

    mount_point = "/home/pc/sys"
    self.log(f"=== [削除処理] 開始 ({app_name}) ===")

    success = False  # 削除成功フラグ

    try:
      self.mount_image(img_path, mount_point)

      target_path = f"{mount_point}/{selected_dest}/{app_name}"

      check_exist = subprocess.run(
          ["sudo", "test", "-d", target_path], capture_output=True
      )
      if check_exist.returncode != 0:
        raise Exception(f"指定されたアプリが見つかりません: {target_path}")

      self.log(f"アプリを削除中: {target_path}")
      subprocess.run(["sudo", "rm", "-rf", target_path], check=True)

      # 変更をディスクに同期
      subprocess.run(["sudo", "sync"], check=True)

      self.log("アプリの削除が正常に完了しました！")
      messagebox.showinfo("成功", f"アプリ '{app_name}' の削除が完了しました。")
      success = True

    except Exception as e:
      self.log(f"[エラー発生]: {e}")
      messagebox.showerror("エラー", f"処理に失敗しました:\n{e}")

    finally:
      self.log("アンマウント処理を実行中...")
      try:
        subprocess.run(["sudo", "umount", mount_point], check=True)
        self.log("アンマウント完了。")
      except Exception as ex:
        self.log(f"アンマウント時のエラー: {ex}")

    if success:
      self.fetch_app_list()

if __name__ == "__main__":
  app = RomPatcherApp()
  app.mainloop()
