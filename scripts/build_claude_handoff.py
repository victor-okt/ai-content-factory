"""Build Claude handoff on GitHub Actions checkout; never include credentials."""
from __future__ import annotations
import os,re,subprocess,sys,zipfile
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"handoff-output"
OUT.mkdir(exist_ok=True)
EXCLUDE_DIR={".git","node_modules",".venv","venv","__pycache__",".next","dist","build","handoff-output",".pytest_cache"}
EXCLUDE_NAMES={".env",".env.local",".env.production",".env.development","id_rsa","id_ed25519","credentials.json","service-account.json","secrets.json","token.json",".npmrc",".pypirc"}
EXCLUDE_SUFFIX={".pem",".key",".p12",".pfx",".sqlite3",".db"}
# Conservative: never archive suspicious credentials, even if they may be harmless examples.
SENSITIVE_NAME=re.compile(r"(?:^|[-_.])(secret|password|credential|private.key|api.key|access.token)(?:[-_.]|$)",re.I)
SECRET_VALUE=re.compile(rb"(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"][^'\"]{8,}['\"])",re.I)

def run(label,command,cwd=ROOT):
    try:
        p=subprocess.run(command,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors="replace",timeout=180)
        return label,p.returncode,"$ "+" ".join(command)+"\n"+p.stdout
    except Exception as exc:
        return label,99,"$ "+" ".join(command)+"\nERROR: "+repr(exc)+"\n"

def main():
    sha=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    checks=[
      run("Python tests",["python","-m","unittest","discover","-s","tests","-v"]),
      run("Node motion tests",["node","--test",*sorted(str(p.relative_to(ROOT)) for p in (ROOT/"motion-video/character-engine").glob("*.test.mjs"))]) if list((ROOT/"motion-video/character-engine").glob("*.test.mjs")) else ("Node motion tests",99,"No *.test.mjs files found\n"),
      run("Office runtime queue tests",["python","-m","unittest","discover","-s",".","-p","test_*.py","-v"],ROOT/"office/runtime")
    ]
    failures=[name for name,code,_ in checks if code!=0]
    log=["CLAUDE HANDOFF TEST REPORT","Generated UTC: "+datetime.now(timezone.utc).isoformat(),"Git commit: "+sha,"Python: "+sys.version,""]
    for name,code,output in checks:log.extend(["="*70,name+" | exit code "+str(code),"="*70,output,""])
    log.append("RESULT: "+("FAILED: "+", ".join(failures) if failures else "ALL REQUESTED COMMANDS PASSED"))
    log.append("If failed: inspect traceback and failing assertion in the corresponding section above; no guessed root cause is claimed.")
    (OUT/"HASIL_TES.txt").write_text("\n".join(log),encoding="utf-8")
    included=[];excluded=[]
    zip_path=OUT/"REPO_MAIN_SANITIZED.zip"
    with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(ROOT.rglob("*")):
            if not p.is_file():continue
            rel=p.relative_to(ROOT)
            if any(part in EXCLUDE_DIR for part in rel.parts) or p.name in EXCLUDE_NAMES or p.suffix.lower() in EXCLUDE_SUFFIX or SENSITIVE_NAME.search(p.name):
                excluded.append(str(rel));continue
            if p.is_symlink():excluded.append(str(rel));continue
            data=p.read_bytes()
            if SECRET_VALUE.search(data):
                excluded.append(str(rel)+" [possible credential content]");continue
            z.writestr(str(rel).replace(os.sep,"/"),data);included.append(str(rel))
    summary=[
      "# STATUS JUJUR — AI Content Factory + VO1995",
      "",
      "Generated on GitHub Actions UTC: "+datetime.now(timezone.utc).isoformat(),
      "Branch: main (checkout on push/workflow_dispatch); SHA: "+sha,
      "",
      "## Verified in this workflow",
      *["- "+name+": "+("PASS" if code==0 else "FAIL")+" (exit "+str(code)+")" for name,code,_ in checks],
      "- Sanitized ZIP created from GitHub checkout; "+str(len(included))+" files included; "+str(len(excluded))+" excluded.",
      "- This workflow does not test the graphical quality of an MP4 or a Windows installation.",
      "",
      "## Code exists but not demonstrated end-to-end",
      "- Pixel Office dashboard; offline template pipeline for six agents.",
      "- VO1995 motion library, puppet bridge and prototype renderer.",
      "- Windows starter and VPS heartbeat worker: not proof of 24-hour autonomous AI.",
      "- ElevenLabs API integration and complete animated video pipeline are not verified.",
      "",
      "## Why the historical 'Tests' workflow failed since commit #74",
      "- This package runs the same Python unittest command; see HASIL_TES.txt for present failures.",
      "- Historical root cause CANNOT be established without logs from the specific failed GitHub Actions run. Do not guess from current results.",
      "",
      "## Media made in earlier ChatGPT sessions",
      "- MP4/GIF/WAV/PNG made in ChatGPT /mnt/data may not be committed to GitHub.",
      "- These are NOT automatically present in this ZIP. They must be transferred separately.",
      "- Approved Kitsune master may exist in ChatGPT Library rather than repository; verify identity before production.",
      "",
      "## Excluded files",
      *["- "+p for p in excluded[:100]],
      ""]
    (OUT/"STATUS_JUJUR.md").write_text("\n".join(summary),encoding="utf-8")
    print("Created",zip_path,"files",len(included),"excluded",len(excluded))
    print("Test failures:",failures)
    # Tests intentionally do not prevent artifact upload: Claude needs the logs even on failure.
if __name__=="__main__":main()
