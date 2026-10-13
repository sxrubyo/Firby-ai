=== FIRBY.PY IMPORTS FROM SATELLITES ===
30:from firby_demo import FirbyDemo
31:from firby_admin import FirbyAdmin, AuthEngine, AdminLearningEngine, SimulationEngine, SelfImprovementEngine
32:from firby_production import FirbyProduction
33:from firby_utils import (
82:    from firby_core import ConversationEngine, PersonaRegistry
83:    from firby_core.first_turn_ops import (
99:    from firby_core.prompt_ops import (
114:    from firby_domino import build_demo_domino_payload
122:    from firby_i18n import get_i18n, detect_user_language, SUPPORTED_LANGUAGES
129:    from firby_session import SessionManager
135:    from firby_audio import AudioHandler
141:    from firby_generator import GeneratorManager
175:    from firby_pitch_upgrade import (
181:    from firby_send_guard import SendGuard, check_proactive_handoff
182:    from firby_nuke_robot_phrases import apply_patch as _nuke_robot_apply
231:    from firby_v9_humanization import (
2482:        from firby_v9_humanization import v9_patch_archetypes, V9_PERSONALITY_ARCHETYPES
2645:        from firby_v9_humanization import v9_enhance_anti_robot_filter
9236:            from firby_brain_v10 import extract_short_memory, format_memory_block
11555:            from firby_intelligence import _trigger_self_improve
12452:                    from firby_commands import get_command_handler
19727:                from firby_commands import get_command_handler
19867:                from firby_demo_voice import generate_demo_audio, should_send_voice_in_demo
20208:        from firby_brain_v10 import init_brain, patch_llm_first
20279:        from firby_memory_engine import memory_engine as _mem_engine
20280:        from firby_cron import init_scheduler as _init_cron
20281:        from firby_uncertainty import uncertainty_detector as _unc_detector
20304:        from firby_cron import shutdown_scheduler
20329:    from firby_admin_api import router as admin_api_router

=== SATELLITES THAT IMPORT FROM FIRBY.PY ===
/home/ubuntu/firby/firby_admin.py:29:        from firby import db, llm_engine
/home/ubuntu/firby/firby_admin.py:86:                from firby import llm_engine as _llm
/home/ubuntu/firby/firby_admin.py:226:        from firby import v8_process_response
/home/ubuntu/firby/firby_admin.py:592:        from firby import db
/home/ubuntu/firby/firby_admin.py:653:        from firby import db
/home/ubuntu/firby/firby_admin.py:668:        from firby import db
/home/ubuntu/firby/firby_admin.py:684:        from firby import db
/home/ubuntu/firby/firby_admin.py:695:        from firby import db
/home/ubuntu/firby/firby_admin.py:702:        from firby import db
/home/ubuntu/firby/firby_admin.py:720:        from firby import db
/home/ubuntu/firby/firby_bridge.py:281:        import firby as firby_module
/home/ubuntu/firby/firby_production.py:21:        from firby import db, llm_engine, kb, v8_process_response

=== EXTERNAL PIP PACKAGES ===
from abc import ABC, abstractmethod
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from collections import defaultdict
from collections import deque as _deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import asynccontextmanager
from dataclasses import dataclass
from dataclasses import dataclass as _dc, field as _dcfield
from dataclasses import dataclass, field
from dataclasses import dataclass, field, asdict
from datetime import datetime
from datetime import datetime as _dt
from datetime import datetime, timedelta
from datetime import datetime, timedelta, timezone
from datetime import datetime, timezone
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from enum import Enum
from enum import Enum, auto
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi import FastAPI, Request, Response, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse as _StreamingResponse
from functools import lru_cache
from functools import lru_cache, wraps
from pathlib import Path
from pydantic import BaseModel, Field
from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.theme import Theme
from typing import (
from typing import Any, Callable, Dict, List, Optional, Tuple
from typing import Any, Callable, Dict, Optional
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional, Tuple
from typing import Any, Iterable, Tuple
from typing import Dict as _D, List as _L, Optional as _Opt
from typing import Dict, List, Optional
from typing import Dict, List, Optional, Any, Set
from typing import Dict, List, Optional, Tuple
from typing import Dict, List, Optional, Tuple, Any
from typing import Dict, List, Set, Tuple
from typing import Dict, Optional
from typing import List, Dict, Optional
from typing import List, Dict, Optional, Tuple, Any
from typing import List, Optional
from typing import List, Optional, Tuple
from typing import Optional
from typing import Optional, Dict, List
from typing import Optional, Tuple
from urllib.parse import urlencode
import argparse
import ast
import asyncio
import asyncio as _obs_asyncio
import asyncio, json, os, subprocess, sys, time
import base64
import curses
import hashlib
import httpx
import json
import json as _obs_json
import json, logging, os
import json, logging, re, time
import json, logging, sqlite3
import logging
import logging, asyncio
import logging, os, tempfile, base64
import math
import os
import os, sys, time, json, subprocess, signal, random
import platform, re, argparse, tarfile, sqlite3, csv
import random
import random as _random
import random as _random_trainer
import re
import re, random, logging
import secrets
import select as _select
import shutil
import sqlite3
import subprocess
import sys
import sys, os, json, time, subprocess, threading, shutil, hashlib, signal, ast, tempfile
import tempfile
import time
import time as _obs_time
import traceback
import uuid
import uuid as _uuid_trainer

=== CIRCULAR RISKS ===
CIRCULAR: firby_admin (imported by firby.py AND imports from it)
CIRCULAR: firby_production (imported by firby.py AND imports from it)
