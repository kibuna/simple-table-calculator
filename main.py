from fastapi import FastAPI, WebSocket, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from typing import Optional, Dict
import json
import csv
import io
import uuid
from datetime import datetime, timedelta

app = FastAPI()

# データモデル
class Row:
    def __init__(self, id: int):
        self.id = id
        self.param: Optional[float] = None
        self.a: Optional[float] = None
        self.b: Optional[float] = None
        self.c: Optional[float] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "param": self.param,
            "a": self.a,
            "b": self.b,
            "c": self.c
        }
    
    def update(self, column: str, value: Optional[float]):
        if value == "":
            value = None
        elif value is not None:
            value = float(value)
        
        if column == "param":
            self.param = value
        elif column == "a":
            self.a = value
            if self.param is not None and value is not None:
                self.b = value + self.param
                self.c = value * self.param
        elif column == "b":
            self.b = value
            if self.param is not None and value is not None:
                self.a = value - self.param
                self.c = self.a * self.param
        elif column == "c":
            self.c = value
            if self.param is not None and value is not None and self.param != 0:
                self.a = value / self.param
                self.b = self.a + self.param

# セッションクラス
class Session:
    def __init__(self):
        self.rows = {1: Row(1), 2: Row(2), 3: Row(3)}
        self.next_id = 4
        self.row_order = [1, 2, 3]
        self.column_order = ["param", "a", "b", "c"]
        self.connections: list[WebSocket] = []
        self.last_access = datetime.now()

# セッション管理
sessions: Dict[str, Session] = {}

# 古いセッションをクリーンアップ（1時間以上アクセスのないもの）
def cleanup_sessions():
    now = datetime.now()
    expired = [sid for sid, session in sessions.items() 
               if now - session.last_access > timedelta(hours=1)]
    for sid in expired:
        del sessions[sid]

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # セッションを取得または作成
    cleanup_sessions()
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    session.connections.append(websocket)
    session.last_access = datetime.now()
    
    # 初期データ送信
    await websocket.send_json({
        "rows": [session.rows[id].to_dict() for id in session.row_order if id in session.rows],
        "column_order": session.column_order
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            session.last_access = datetime.now()
            
            if data["action"] == "update":
                row_id = data["row_id"]
                column = data["column"]
                value = data["value"]
                
                if row_id in session.rows:
                    session.rows[row_id].update(column, value)
                    
                    # 同じセッションの全接続にブロードキャスト
                    for connection in session.connections:
                        await connection.send_json({
                            "rows": [session.rows[id].to_dict() for id in session.row_order if id in session.rows],
                            "column_order": session.column_order
                        })
            
            elif data["action"] == "add_row":
                session.rows[session.next_id] = Row(session.next_id)
                session.row_order.append(session.next_id)
                session.next_id += 1
                
                # 同じセッションの全接続にブロードキャスト
                for connection in session.connections:
                    await connection.send_json({
                        "rows": [session.rows[id].to_dict() for id in session.row_order if id in session.rows],
                        "column_order": session.column_order
                    })
            
            elif data["action"] == "reorder_rows":
                session.row_order[:] = data["order"]
                
                # 同じセッションの全接続にブロードキャスト
                for connection in session.connections:
                    await connection.send_json({
                        "rows": [session.rows[id].to_dict() for id in session.row_order if id in session.rows],
                        "column_order": session.column_order
                    })
            
            elif data["action"] == "reorder_columns":
                session.column_order[:] = data["order"]
                
                # 同じセッションの全接続にブロードキャスト
                for connection in session.connections:
                    await connection.send_json({
                        "rows": [session.rows[id].to_dict() for id in session.row_order if id in session.rows],
                        "column_order": session.column_order
                    })
            
            elif data["action"] == "refresh":
                # 単純に現在のデータを送信
                await websocket.send_json({
                    "rows": [session.rows[id].to_dict() for id in session.row_order if id in session.rows],
                    "column_order": session.column_order
                })
    
    except Exception:
        session.connections.remove(websocket)
        # セッションに接続がなくなったら削除を検討
        if not session.connections:
            session.last_access = datetime.now()  # クリーンアップまで猶予を与える

# CSVダウンロード
@app.get("/download-csv/{session_id}")
async def download_csv(session_id: str):
    if session_id not in sessions:
        return Response(content="Session not found", status_code=404)
    
    session = sessions[session_id]
    output = io.StringIO()
    writer = csv.writer(output)
    
    # ヘッダー行
    headers = ["行"] + [col.upper() for col in session.column_order]
    writer.writerow(headers)
    
    # データ行
    for row_id in session.row_order:
        if row_id in session.rows:
            row = session.rows[row_id]
            row_data = [row_id]
            for col in session.column_order:
                value = getattr(row, col)
                row_data.append(value if value is not None else "")
            writer.writerow(row_data)
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=table_data.csv"}
    )

# 静的ファイル配信
app.mount("/", StaticFiles(directory="static", html=True), name="static")