#!/usr/bin/env python3
"""
EDF診断アプリ ローカルサーバー起動スクリプト
同一Wi-Fi上のスマホからQRコードでアクセス可能にする
"""

import http.server
import socket
import threading
import webbrowser
import os
import sys

PORT = 8765

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def print_qr_terminal(url):
    try:
        import segno
        qr = segno.make(url, error="M")
        print("\n" + "─" * 50)
        print("  📱 スマホでQRコードを読み取ってください")
        print("─" * 50 + "\n")
        qr.terminal(compact=True)
        print()
    except ImportError:
        print("  (QRコード表示にはsegnoが必要です: pip3 install segno)")

def save_qr_image(url, path):
    try:
        import segno
        qr = segno.make(url, error="M")
        qr.save(path, scale=8, border=2, dark="#CC0000", light="#000000")
        return True
    except Exception as e:
        print(f"  QR画像の保存に失敗: {e}")
        return False

def main():
    # サーバーのルートをこのファイルのディレクトリに設定
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    ip  = get_local_ip()
    url = f"http://{ip}:{PORT}/index.html"

    # HTTPサーバー起動
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None  # アクセスログを抑制

    server = http.server.HTTPServer(("0.0.0.0", PORT), handler)

    print("\n" + "═" * 52)
    print("  EDF 隊員適性診断システム — サーバー起動中")
    print("═" * 52)
    print(f"\n  ✅ サーバーURL : {url}")
    print(f"  🖥  PC用URL    : http://localhost:{PORT}/index.html")
    print(f"\n  ⚠  このPCと同じWi-Fiに接続したスマホで")
    print(f"     下記のQRコードを読み取ってください。")
    print(f"\n  🛑 停止するには Ctrl+C を押してください\n")

    # ターミナルにQR表示
    print_qr_terminal(url)

    # QR画像をHTMLで表示するページも生成
    qr_img_path = os.path.join(base_dir, "qr.png")
    if save_qr_image(url, qr_img_path):
        # QR確認用HTMLを生成
        qr_html_path = os.path.join(base_dir, "qr_access.html")
        with open(qr_html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EDF診断 — アクセスQRコード</title>
  <style>
    body {{ background:#000; color:#ccc; font-family:'Courier New',monospace;
           display:flex; flex-direction:column; align-items:center;
           justify-content:center; min-height:100vh; margin:0; padding:20px; text-align:center; }}
    h1   {{ color:#FFD700; font-size:20px; letter-spacing:4px; margin-bottom:8px; }}
    p    {{ font-size:12px; letter-spacing:2px; color:#888; margin-bottom:24px; }}
    .qr  {{ background:#000; padding:16px; border:2px solid #CC0000;
            box-shadow:0 0 30px rgba(204,0,0,.4); }}
    .qr img {{ display:block; width:240px; height:240px; image-rendering:pixelated; }}
    .url {{ margin-top:20px; background:#0a0a0a; border:1px solid #333;
            padding:12px 20px; font-size:13px; color:#CC0000; word-break:break-all; }}
    .note {{ margin-top:16px; font-size:11px; color:#555; }}
  </style>
</head>
<body>
  <h1>EDF 隊員適性診断</h1>
  <p>スマホで読み取ってください / SCAN TO PLAY</p>
  <div class="qr"><img src="qr.png" alt="QR Code"></div>
  <div class="url">{url}</div>
  <p class="note">同じWi-Fiに接続したスマホのカメラで読み取り</p>
</body>
</html>""")
        print(f"  📄 QR確認ページ: http://localhost:{PORT}/qr_access.html\n")
        # PC用QRページをブラウザで開く
        threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{PORT}/qr_access.html")).start()

    print("─" * 52)
    print("  サーバー稼働中... アクセス待ち受け中")
    print("─" * 52 + "\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n  サーバーを停止しました。お疲れ様でした。EDF!\n")
        server.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()
