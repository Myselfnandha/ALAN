# alan_core/runtime.py
from alan_app.alan_core_engine import AlanCore  # uses the engine you already have
import argparse, json

def repl(core: AlanCore):
    print("Alan REPL — type 'exit' to quit")
    while True:
        raw = input(">> ").strip()
        if raw.lower() in ("exit","quit"): break
        out = core.process(raw)
        print(out)

def run_once(core: AlanCore, text: str):
    print(core.process(text))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repl", action="store_true")
    parser.add_argument("--text", type=str, default=None)
    args = parser.parse_args()
    core = AlanCore()
    if args.repl:
        repl(core)
    elif args.text:
        run_once(core, args.text)
    else:
        repl(core)
