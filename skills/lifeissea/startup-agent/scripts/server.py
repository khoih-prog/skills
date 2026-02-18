#!/usr/bin/env python3
"""
Raon OS — HTTP API Server
로컬 REST API로 사업계획서 평가 기능 제공.
웹챗/k-startup.ai 임베드용.

Usage:
    python server.py [--port 8400] [--model qwen3:8b]
    raon.sh serve [--port 8400]

Endpoints:
    POST /v1/evaluate   — 사업계획서 평가
    POST /v1/improve    — 사업계획서 개선
    POST /v1/match      — 정부 지원사업 매칭
    POST /v1/draft      — 지원서 초안 생성
    POST /v1/checklist  — 지원 준비 점검
    POST /v1/chat       — 대화형 평가 세션 (멀티턴)
    GET  /health        — 헬스체크
    GET  /v1/modes      — 지원 모드 목록
"""

import base64
import json
import os
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import sys
import tempfile
import time
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# evaluate.py의 함수들 import
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# ─── KakaoWebhook import (폴백 포함) ─────────────────────────────────────────
_KAKAO_AVAILABLE = False
try:
    from kakao_webhook import KakaoWebhook as _KakaoWebhook
    _KAKAO_AVAILABLE = True
except ImportError as _ke:
    print(f"[raon-server] KakaoWebhook 로드 실패: {_ke}", file=sys.stderr)

# 전역 카카오 핸들러 인스턴스 (lazy init)
_kakao_handler = None

from evaluate import (
    build_prompt,
    build_comparison_prompt,
    build_followup_prompt,
    call_ollama,
    call_raon_api,
    parse_score,
    fix_score_text,
    RAON_API_URL,
    RAON_API_KEY,
)

# In-memory chat sessions: session_id -> {history: [], original_text: str, model: str}
CHAT_SESSIONS = {}

DEFAULT_PORT = 8400
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "")

# --- Data directory ---
DATA_DIR = Path(SCRIPT_DIR) / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
API_KEYS_FILE = DATA_DIR / "api_keys.json"
USAGE_FILE = DATA_DIR / "usage.json"

_data_lock = threading.Lock()

# Rate limits per plan: {plan: {generate: N, chat: N}}
PLAN_LIMITS = {
    "free":     {"generate": 5,  "chat": 20},
    "pro":      {"generate": 20, "chat": 100},
    "lifetime": {"generate": 20, "chat": 100},
}

# Which endpoints count as "generate" vs "chat"
GENERATE_ENDPOINTS = {"evaluate", "improve", "match", "draft", "checklist", "investor", "valuation", "idea/suggest"}
CHAT_ENDPOINTS = {"chat"}


def _load_json(path):
    # type: (Path) -> Any
    if path.exists():
        with open(str(path), "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_json(path, data):
    # type: (Path, Any) -> None
    with open(str(path), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_api_keys():
    # type: () -> Dict[str, Any]
    """Returns {key_string: key_obj}"""
    raw = _load_json(API_KEYS_FILE)
    if isinstance(raw, list):
        return {k["key"]: k for k in raw}
    return raw


def _save_api_keys(keys_dict):
    # type: (Dict[str, Any]) -> None
    _save_json(API_KEYS_FILE, keys_dict)


def _load_usage():
    # type: () -> Dict[str, Any]
    return _load_json(USAGE_FILE)


def _save_usage(usage):
    # type: (Dict[str, Any]) -> None
    _save_json(USAGE_FILE, usage)


def _today_str():
    # type: () -> str
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _check_rate_limit(api_key, endpoint_category):
    # type: (str, str) -> Optional[str]
    """Returns None if OK, or error message if limit exceeded."""
    with _data_lock:
        keys = _load_api_keys()
        key_obj = keys.get(api_key)
        if not key_obj:
            return "invalid_api_key"
        if not key_obj.get("active", True):
            return "api_key_disabled"
        plan = key_obj.get("plan", "free")
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        limit_val = limits.get(endpoint_category, 0)
        if limit_val == 0:
            return None  # no limit for this category

        usage = _load_usage()
        today = _today_str()
        key_usage = usage.get(api_key, {}).get(today, {})
        current = key_usage.get(endpoint_category, 0)
        if current >= limit_val:
            return "rate_limit_exceeded: {}/{} {} calls used. Resets at midnight UTC.".format(
                current, limit_val, endpoint_category
            )
    return None


def _increment_usage(api_key, endpoint_category, tokens_in=0, tokens_out=0):
    # type: (str, str, int, int) -> None
    with _data_lock:
        usage = _load_usage()
        today = _today_str()
        if api_key not in usage:
            usage[api_key] = {}
        if today not in usage[api_key]:
            usage[api_key][today] = {"generate": 0, "chat": 0, "tokens_in": 0, "tokens_out": 0}
        day = usage[api_key][today]
        day[endpoint_category] = day.get(endpoint_category, 0) + 1
        day["tokens_in"] = day.get("tokens_in", 0) + tokens_in
        day["tokens_out"] = day.get("tokens_out", 0) + tokens_out
        _save_usage(usage)


def _is_localhost(handler):
    # type: (Any) -> bool
    addr = handler.client_address[0] if handler.client_address else ""
    return addr in ("127.0.0.1", "::1", "localhost")


def _generate_api_key():
    # type: () -> str
    return "rk_" + secrets.token_hex(24)

VALID_MODES = ["evaluate", "improve", "match", "draft", "checklist", "investor", "valuation", "idea"]

from valuation import estimate_valuation
from gamification import add_xp, load_profile, save_profile, format_profile, _default_profile
from idea import list_categories, get_category_detail, suggest_ideas

# ─── AgenticRAG import (폴백 포함) ───────────────────────────────────────────
_AGENTIC_RAG_AVAILABLE = False
try:
    from agentic_rag import AgenticRAG as _AgenticRAG
    import rag_pipeline as _rag_module
    _AGENTIC_RAG_AVAILABLE = True
except ImportError as _e:
    print(f"[raon-server] AgenticRAG 로드 실패 (기본 모드로 동작): {_e}", file=sys.stderr)


def extract_text_from_pdf(b64data: str) -> str:
    """Base64 PDF → text using pypdf (fallback: PyPDF2, pdfplumber)."""
    raw = base64.b64decode(b64data)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(raw)
        tmp = f.name
    try:
        # pypdf first
        try:
            from pypdf import PdfReader
            reader = PdfReader(tmp)
            return "\n".join(p.extract_text() or "" for p in reader.pages).strip()
        except ImportError:
            pass
        # PyPDF2 fallback
        try:
            from PyPDF2 import PdfReader as PdfReader2
            reader = PdfReader2(tmp)
            return "\n".join(p.extract_text() or "" for p in reader.pages).strip()
        except ImportError:
            pass
        # pdfplumber fallback
        import pdfplumber
        with pdfplumber.open(tmp) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages).strip()
    finally:
        os.unlink(tmp)


class RaonHandler(BaseHTTPRequestHandler):
    model = DEFAULT_MODEL

    def log_message(self, format, *args):
        """간결한 로그"""
        print(f"[raon-api] {args[0]}")

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status, message):
        self._send_json({"error": message}, status)

    def _handle_chat(self):
        """POST /v1/chat — 세션 기반 대화형 평가"""
        import uuid as _uuid

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_error(400, "empty_body")
            return

        try:
            body = json.loads(self.rfile.read(content_length))
        except json.JSONDecodeError:
            self._send_error(400, "invalid_json")
            return

        session_id = body.get("session_id", "")
        message = body.get("message", "").strip()
        model = body.get("model", self.model)

        # New session: requires text or pdf_base64
        if not session_id or session_id not in CHAT_SESSIONS:
            text = body.get("text", "").strip()
            pdf_b64 = body.get("pdf_base64", "").strip()

            if pdf_b64 and not text:
                try:
                    text = extract_text_from_pdf(pdf_b64)
                except Exception as e:
                    self._send_error(400, f"pdf_parse_error: {e}")
                    return

            if not text:
                self._send_error(400, "new session requires 'text' or 'pdf_base64'")
                return

            session_id = session_id or str(_uuid.uuid4())

            # Run initial evaluation
            start = time.time()
            prompt = build_prompt(text, mode="evaluate")
            result = None
            if RAON_API_URL and RAON_API_KEY:
                result = call_raon_api(text, "evaluate")
            if not result:
                result = call_ollama(prompt, model)

            if not result:
                self._send_error(503, "llm_unavailable")
                return

            CHAT_SESSIONS[session_id] = {
                "history": [{"role": "assistant", "content": result}],
                "original_text": text,
                "model": model,
            }

            result = fix_score_text(result)
            score = parse_score(result)
            resp = {
                "status": "ok",
                "session_id": session_id,
                "message": result,
                "turn": 0,
                "duration": round(time.time() - start, 2),
            }
            if score is not None:
                resp["score"] = score
            self._track_usage(tokens_in=len(text), tokens_out=len(result))
            self._send_json(resp)
            return

        # Existing session: follow-up
        if not message:
            self._send_error(400, "missing 'message' for follow-up")
            return

        session = CHAT_SESSIONS[session_id]
        session["history"].append({"role": "user", "content": message})

        start = time.time()
        answer = None
        strategy_used = "followup"

        # ── AgenticRAG 시도 (RAG 벡터 저장소가 있을 때만) ──
        if _AGENTIC_RAG_AVAILABLE:
            try:
                _store = _rag_module.load_vector_store()
                if _store:
                    _agentic = _AgenticRAG(_rag_module)
                    _agentic_result = _agentic.run(message)
                    answer = _agentic_result.get("answer", "")
                    strategy_used = _agentic_result.get("strategy_used", "agentic")
                    print(f"[agentic-rag] strategy={strategy_used}", file=sys.stderr)
            except Exception as _ae:
                print(f"[agentic-rag] 실패, 기본 모드로: {_ae}", file=sys.stderr)
                answer = None

        # ── 기존 Ollama 폴백 ──
        if not answer:
            followup_prompt = build_followup_prompt(
                session["history"], message, session["original_text"]
            )
            answer = call_ollama(followup_prompt, session.get("model", model))

        if not answer:
            session["history"].pop()  # rollback
            self._send_error(503, "llm_unavailable")
            return

        session["history"].append({"role": "assistant", "content": answer})

        self._track_usage(tokens_in=len(message), tokens_out=len(answer))
        self._send_json({
            "status": "ok",
            "session_id": session_id,
            "message": answer,
            "turn": len([h for h in session["history"] if h["role"] == "user"]),
            "duration": round(time.time() - start, 2),
            "strategy": strategy_used,
        })

    def _get_api_key(self):
        # type: () -> Optional[str]
        """Extract API key from header or query param."""
        key = self.headers.get("X-API-Key", "")
        if key:
            return key
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        keys = qs.get("api_key", [])
        if keys:
            return keys[0]
        return None

    def _authenticate(self, endpoint_category):
        # type: (Optional[str]) -> bool
        """Returns True if request is authorized. Sends error response if not."""
        # Skip auth for localhost (widget dev)
        if _is_localhost(self):
            return True
        api_key = self._get_api_key()
        if not api_key:
            self._send_error(401, "missing api key: provide X-API-Key header or ?api_key= param")
            return False
        with _data_lock:
            keys = _load_api_keys()
        key_obj = keys.get(api_key)
        if not key_obj or not key_obj.get("active", True):
            self._send_error(401, "invalid or disabled api key")
            return False
        # Rate limit check
        if endpoint_category:
            err = _check_rate_limit(api_key, endpoint_category)
            if err and "rate_limit_exceeded" in err:
                self._send_json({"error": err, "retry_after": "midnight UTC"}, 429)
                return False
        # Store key on handler for usage tracking
        self._current_api_key = api_key
        self._current_endpoint_category = endpoint_category
        return True

    def _track_usage(self, tokens_in=0, tokens_out=0):
        # type: (int, int) -> None
        api_key = getattr(self, "_current_api_key", None)
        cat = getattr(self, "_current_endpoint_category", None)
        if api_key and cat:
            _increment_usage(api_key, cat, tokens_in, tokens_out)

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
        self.end_headers()

    def do_DELETE(self):
        """DELETE /api/keys/:key — deactivate key (admin only)"""
        path = urlparse(self.path).path
        if path.startswith("/api/keys/"):
            admin = self.headers.get("X-API-Key", "") or self.headers.get("Authorization", "").replace("Bearer ", "")
            if not ADMIN_KEY or admin != ADMIN_KEY:
                self._send_error(403, "admin key required")
                return
            target_key = path.split("/api/keys/")[1].split("/")[0]
            with _data_lock:
                keys = _load_api_keys()
                if target_key not in keys:
                    self._send_error(404, "key not found")
                    return
                keys[target_key]["active"] = False
                _save_api_keys(keys)
            self._send_json({"status": "ok", "key": target_key, "active": False})
        else:
            self._send_error(404, "not_found")

    def do_GET(self):
        path = urlparse(self.path).path

        # Admin: GET /api/keys/:key/usage
        if path.startswith("/api/keys/") and path.endswith("/usage"):
            target_key = path.split("/api/keys/")[1].split("/usage")[0]
            requester = self._get_api_key() or ""
            if requester != target_key:
                if not ADMIN_KEY or requester != ADMIN_KEY:
                    self._send_error(403, "forbidden")
                    return
            with _data_lock:
                usage = _load_usage()
            key_usage = usage.get(target_key, {})
            self._send_json({"status": "ok", "key": target_key, "usage": key_usage})
            return

        if path == "/health":
            self._send_json({
                "status": "ok",
                "version": "0.3.4",
                "model": self.model,
            })
        elif path == "/" or path == "/index.html":
            widget_path = Path(__file__).resolve().parent.parent / "widget" / "raon-chat.html"
            if widget_path.exists():
                body = widget_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self._send_error(404, "widget not found")
        elif path.startswith("/widget/"):
            widget_dir = Path(__file__).resolve().parent.parent / "widget"
            file_path = widget_dir / path[8:]
            if file_path.exists() and file_path.is_file():
                body = file_path.read_bytes()
                ct = "application/javascript" if str(file_path).endswith(".js") else "text/plain"
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self._send_error(404, "not_found")
        elif path.startswith("/v1/"):
            # Auth required for all /v1/ GET endpoints
            if not self._authenticate(None):
                return
            if path == "/v1/modes":
                self._send_json({
                    "modes": VALID_MODES,
                    "description": {
                        "evaluate": "사업계획서 평가 (TIPS 기준 100점 만점)",
                        "improve": "사업계획서 개선안 작성",
                        "match": "정부 지원사업 매칭 (가중치 기반)",
                        "draft": "지원서 초안 자동 생성 (--program 필수)",
                        "checklist": "지원 준비 상태 점검 (--program 필수)",
                        "investor": "투자자 관점 프로필 및 매칭 전략 (Factsheet AI)",
                        "valuation": "Pre-Seed~Series A 밸류에이션 자동 산출 (Scorecard/Berkus/Revenue Multiple)",
                    }
                })
            elif path == "/v1/idea" or path == "/v1/idea/list":
                cats = list_categories()
                self._send_json({"status": "ok", "categories": cats})
            elif path.startswith("/v1/idea/detail/"):
                try:
                    cat_id = int(path.split("/")[-1])
                except ValueError:
                    self._send_error(400, "invalid category id")
                    return
                cat = get_category_detail(cat_id)
                if cat:
                    self._send_json({"status": "ok", "category": cat})
                else:
                    self._send_error(404, "category {} not found".format(cat_id))
            elif path == "/v1/profile":
                profile = load_profile()
                self._send_json({"status": "ok", "profile": profile})
            else:
                self._send_error(404, "not_found")
        else:
            self._send_error(404, "not_found")

    def _handle_kakao(self):
        """POST /kakao — 카카오 i 오픈빌더 웹훅 처리."""
        global _kakao_handler

        # 카카오는 반드시 200 응답 필요 — 에러도 정상 응답으로
        def kakao_error_response(msg="잠시 후 다시 시도해주세요 😊"):
            return {
                "version": "2.0",
                "template": {
                    "outputs": [{"simpleText": {"text": msg}}],
                },
            }

        if not _KAKAO_AVAILABLE:
            self._send_json(kakao_error_response("서비스 준비 중입니다."))
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = b""
        if content_length > 0:
            body_bytes = self.rfile.read(content_length)

        # 서명 검증
        sig = self.headers.get("X-Hub-Signature", "")
        if _kakao_handler is None:
            # AgenticRAG 인스턴스 연결 시도
            rag_instance = None
            if _AGENTIC_RAG_AVAILABLE:
                try:
                    _store = _rag_module.load_vector_store()
                    if _store:
                        rag_instance = _AgenticRAG(_rag_module)
                except Exception:
                    pass
            _kakao_handler = _KakaoWebhook(rag=rag_instance)

        if not _kakao_handler.verify_signature(body_bytes, sig):
            self._send_json({"error": "invalid signature"}, 401)
            return

        try:
            kakao_body = json.loads(body_bytes) if body_bytes else {}
            response = _kakao_handler.process(kakao_body)
            self._send_json(response)
        except Exception as e:
            print(f"[raon-server] /kakao 처리 오류: {e}", file=sys.stderr)
            self._send_json(kakao_error_response())

    def do_POST(self):
        path = urlparse(self.path).path

        # 카카오 웹훅 엔드포인트 (인증 불필요)
        if path == "/kakao":
            self._handle_kakao()
            return

        # Admin: POST /api/keys — create new API key
        if path == "/api/keys":
            admin = self.headers.get("X-API-Key", "") or self.headers.get("Authorization", "").replace("Bearer ", "")
            if not ADMIN_KEY or admin != ADMIN_KEY:
                self._send_error(403, "admin key required (set ADMIN_KEY env var)")
                return
            content_length = int(self.headers.get("Content-Length", 0))
            body = {}
            if content_length > 0:
                try:
                    body = json.loads(self.rfile.read(content_length))
                except json.JSONDecodeError:
                    self._send_error(400, "invalid_json")
                    return
            new_key = _generate_api_key()
            key_obj = {
                "key": new_key,
                "user_id": body.get("user_id", ""),
                "plan": body.get("plan", "free"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "active": True,
            }
            with _data_lock:
                keys = _load_api_keys()
                keys[new_key] = key_obj
                _save_api_keys(keys)
            self._send_json({"status": "ok", "key": key_obj})
            return

        # Extract mode from path: /v1/evaluate -> evaluate
        if not path.startswith("/v1/"):
            self._send_error(404, "not_found")
            return

        mode = path[4:]  # strip "/v1/"

        # Determine endpoint category for rate limiting
        if mode in CHAT_ENDPOINTS:
            _ep_cat = "chat"
        elif mode in GENERATE_ENDPOINTS:
            _ep_cat = "generate"
        else:
            _ep_cat = "generate"  # default

        # Auth middleware for all /v1/ POST endpoints
        if not self._authenticate(_ep_cat):
            return

        # Profile reset
        if path == "/v1/profile/reset":
            save_profile(_default_profile())
            self._send_json({"status": "ok", "message": "profile_reset"})
            return

        # Idea suggest endpoint
        if path == "/v1/idea/suggest":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_error(400, "empty_body")
                return
            try:
                body = json.loads(self.rfile.read(content_length))
            except json.JSONDecodeError:
                self._send_error(400, "invalid_json")
                return
            bg = body.get("background", "")
            interests = body.get("interests", "")
            result = suggest_ideas(bg, interests)
            # 아이디어 탐색도 XP 적립
            try:
                gami = add_xp("idea", {})
                result["xp_gained"] = gami.get("xp_gained", 0)
                result["level"] = gami.get("level", 1)
            except Exception:
                pass
            self._track_usage()
            self._send_json({"status": "ok", **result})
            return

        # Chat endpoint
        if mode == "chat":
            self._handle_chat()
            return

        if mode not in VALID_MODES:
            self._send_error(400, f"invalid_mode: {mode}. Valid: {VALID_MODES}")
            return

        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_error(400, "empty_body")
            return

        try:
            body = json.loads(self.rfile.read(content_length))
        except json.JSONDecodeError:
            self._send_error(400, "invalid_json")
            return

        text = body.get("text", "").strip()
        pdf_b64 = body.get("pdf_base64", "").strip()
        program = body.get("program", "TIPS")
        model = body.get("model", self.model)

        # PDF base64 → text extraction
        if pdf_b64 and not text:
            try:
                text = extract_text_from_pdf(pdf_b64)
            except Exception as e:
                self._send_error(400, f"pdf_parse_error: {e}")
                return

        # Valuation mode: direct computation, no LLM needed
        if mode == "valuation":
            try:
                result = estimate_valuation(
                    stage=body.get("stage", "seed"),
                    industry=body.get("industry", "default"),
                    revenue=float(body.get("revenue", 0)),
                    mrr=float(body.get("mrr", 0)),
                    tips=bool(body.get("tips", False)),
                    gov_rnd=float(body.get("gov_rnd", 0)),
                    scorecard_scores=body.get("scorecard_scores"),
                    berkus_scores=body.get("berkus_scores"),
                )
                self._track_usage()
                self._send_json(result)
            except Exception as e:
                self._send_error(400, "valuation_error: {}".format(e))
            return

        if not text:
            self._send_error(400, "missing_text (provide 'text' or 'pdf_base64')")
            return

        if mode in ("draft", "checklist") and not program:
            # 아이디어에서 넘어온 경우 text에서 program 추출 시도
            import re as _re
            m = _re.search(r'\[아이디어:\s*([^\]]+)\]', text or '')
            if m:
                program = m.group(1).strip()
            else:
                program = "TIPS"  # 기본값

        # Run evaluation
        start = time.time()
        result = None

        # 1st: K-Startup AI API
        if RAON_API_URL and RAON_API_KEY:
            result = call_raon_api(text, mode)

        # 2nd: Ollama fallback
        if not result:
            prompt = build_prompt(text, mode, program=program)
            result = call_ollama(prompt, model)

        duration = round(time.time() - start, 2)

        if not result:
            self._send_error(503, "llm_unavailable")
            return

        # Fix score mismatch and parse
        result = fix_score_text(result)
        score = parse_score(result)

        # Gamification
        gami_action = mode
        if mode == "checklist":
            gami_action = "checklist_complete"
        gami_ctx = {}
        if score is not None:
            gami_ctx["score"] = score
        try:
            gami_result = add_xp(gami_action, gami_ctx)
        except Exception:
            gami_result = None

        response = {
            "status": "ok",
            "mode": mode,
            "model": model,
            "text_length": len(text),
            "duration": duration,
            "result": result,
        }
        if score is not None:
            response["score"] = score
        if gami_result:
            response["xp_gained"] = gami_result["xp_gained"]
            response["level"] = gami_result["level"]
            response["title"] = gami_result["title"]
            response["new_badges"] = gami_result["new_badges"]

        # Log to history.jsonl
        try:
            log_entry = {
                "timestamp": int(start),
                "mode": mode,
                "model": model,
                "input_len": len(text),
                "duration": duration,
                "status": "success" if result else "fail",
            }
            if score is not None:
                log_entry["score"] = score
            hist_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history.jsonl")
            with open(hist_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass

        self._track_usage(tokens_in=len(text), tokens_out=len(result))
        self._send_json(response)


def main():
    parser = argparse.ArgumentParser(description="🌅 Raon OS API Server")
    parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT)
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    RaonHandler.model = args.model

    server = HTTPServer((args.host, args.port), RaonHandler)
    print(f"🌅 Raon OS API Server running on http://{args.host}:{args.port}")
    print(f"   Model: {args.model}")
    print(f"   Endpoints: GET /health, /v1/modes | POST /v1/{{evaluate,improve,match,draft,checklist}}")
    print(f"   Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.server_close()


if __name__ == "__main__":
    main()
