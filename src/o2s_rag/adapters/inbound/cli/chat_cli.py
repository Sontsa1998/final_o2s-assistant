"""Chat en terminal avec streaming et affichage du cheminement : `o2s-chat [--thread ID] [--trace]`.

Commandes : /new (nouveau thread), /history (tours du thread), /quit
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid

DIM, BOLD, YELLOW, RESET = "\033[2m", "\033[1m", "\033[33m", "\033[0m"


async def run(thread_id: str, show_trace: bool) -> None:
    from o2s_rag.bootstrap.container import agent_service
    async with agent_service() as svc:
        print(f"{BOLD}Assistant O2S V4{RESET} — thread {thread_id}  (/new, /history, /quit)")
        while True:
            try:
                q = input(f"\n{BOLD}Vous ›{RESET} ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not q:
                continue
            if q == "/quit":
                break
            if q == "/new":
                thread_id = str(uuid.uuid4())
                print(f"{DIM}Nouveau thread : {thread_id}{RESET}")
                continue
            if q == "/history":
                h = await svc.thread_history(thread_id)
                for t in h["turns"]:
                    print(f"- [{t['status']}] {t['question']} → intention={t['intent']} "
                          f"({t['latency_ms']} ms, ${t['cost_usd']}) chemin="
                          f"{' → '.join(x['node'] for x in t['trace'])}")
                continue
            print(f"{BOLD}O2S ›{RESET} ", end="", flush=True)
            async for ev in svc.stream(q, thread_id):
                t = ev["type"]
                if t == "token":
                    print(ev["content"], end="", flush=True)
                elif t == "node_end" and show_trace:
                    details = {k: v for k, v in ev.items() if k not in {"type", "node"}}
                    print(f"\n{DIM}  ↳ {ev['node']} {json.dumps(details, ensure_ascii=False)[:300]}{RESET}",
                          file=sys.stderr, flush=True)
                elif t == "answer_retracted":
                    print(f"\n{YELLOW}⚠ {ev['reason']}{RESET}")
                elif t == "final":
                    srcs = ", ".join(f"{s['sid']}={s['breadcrumb']}" for s in ev["sources"]
                                     if s["sid"] in ev["citations"])
                    print(f"\n{DIM}[{ev['status']} · intention={ev['analysis'].get('intent')} · "
                          f"{ev['latency_ms']} ms · TTFT {ev.get('ttft_ms')} ms · ${ev['cost_usd']}]{RESET}")
                    if srcs:
                        print(f"{DIM}Sources : {srcs}{RESET}")


def main() -> None:
    from o2s_rag.adapters.inbound.cli import utf8_console
    utf8_console()
    p = argparse.ArgumentParser()
    p.add_argument("--thread", default=None, help="reprendre un thread existant (mémoire)")
    p.add_argument("--trace", action="store_true", help="afficher le cheminement nœud par nœud")
    a = p.parse_args()
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run(a.thread or str(uuid.uuid4()), a.trace))


if __name__ == "__main__":
    main()
