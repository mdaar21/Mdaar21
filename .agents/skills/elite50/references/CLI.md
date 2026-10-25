# CLI and trust boundary

Run `python scripts/engine.py --help` and each command's `--help` for exact options.

Typical flow: init → snapshot → evidence → register → assign → vote → objection/resolve → stage → report.
Use a separate persistent project directory, never the installed skill directory, for actual project state. Use absolute artifact paths where possible. Preserve that directory with the project repository. Project state is stored locally; it is not automatically an external database.

The coordinator supplies real runtime IDs returned by the host and imports actual expert responses. The engine checks uniqueness and registration, but cannot prove an ID came from a real model. An authorized operator can edit local state; this is not an adversarial identity or immutability service. A file digest proves unchanged bytes, not factual accuracy. Reviewers must inspect evidence quality, scope and permissions.

Use `python -m unittest discover -s tests -v` in the skill directory to run synthetic engine checks. Fixtures do not count toward a live project's consensus. Inspect tests before reuse. Preserve real executed test logs as evidence and never mark tests passed from proposed commands alone.

Installed files: SKILL.md, AGENTS.md, agents/openai.yaml, 50 agents/experts/*.md definitions (with additional council-local copies), references/experts.json, workflow.md, CLI.md, scripts/engine.py and tests/test_engine.py. The ten councils and six shared systems are separate sibling skill directories, each with SKILL.md and agents/openai.yaml.

## Example session

```bash
python scripts/engine.py init --project /path/to/project/review --task 'Review the release against acceptance criteria'
python scripts/engine.py snapshot --project /path/to/project/review --version v1 --files /path/to/project/app.py
python scripts/engine.py evidence --project /path/to/project/review --id test-run --file /path/to/project/test-output.txt --description 'Executed test output with command and exit status'
python scripts/engine.py assign --project /path/to/project/review --output /path/to/project/packets
```

Spawn each task packet with its expert definition using the actual host agent API. Record the returned runtime ID with `register --expert <roster-id> --runtime <returned-id>`. Collect the actual response before importing its vote. Each vote must explicitly include the reviewer's `--version v1 --digest <digest-from-task-packet>`, `--decision`, `--reason` and relevant `--evidence` IDs. Stale reviewer responses are rejected. Preserve the original response as an evidence file before import. Reassessments that change decision or version require `--change-code` and `--change-reason`.

Mark each required stage with `stage --name <stage> --evidence <executed-output-id>`. The engine checks evidence integrity, not whether the content actually proves the stage passed: the reviewer and trusted coordinator must inspect it. Finally run `report --project <directory> --output <report.json>`.

The engine uses `fcntl` locks and therefore targets Linux/macOS or WSL. Native Windows needs a lock adapter before use. No model provider credentials, paid service, remote deployment or background service is provisioned by this skill.

Every objection or resolution invalidates votes recorded before that event. Collect fifty fresh final votes after resolving objections; closing an objection alone cannot restore old consensus. Obsolete unused evidence is listed separately as Historical Invalid Evidence and does not block a newer version. The six named stage gates are mandatory for APPROVED; the other workflow phases are coordinator procedures rather than independently authenticated machine checks.

Read build-verification.json for the installation's actual test output, generated-file inventory and hashes. It records PENDING and 0/50: implementation/validation workers are not fifty expert approvals.
