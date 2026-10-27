// `party` command line: parses arguments, calls the booth core, prints results and
// returns the exit code: 0 ok / message received / listen: messages waiting (take them with read) /
// --check nothing to do, 1 unexpected error,
// 2 usage error or refused, 3 wait/listen timeout, 4 should not listen (stopped or closed),
// 5 --check: action needed, 6 listen: a listener is already running (do not start another).
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { DEFAULT_WAIT_TIMEOUT_SEC, initBooth, openBooth, PartyError, type StationDeps, type WaitResult } from './room.ts';
import { formatDelivery, formatJoined, formatNotice, formatRoomClosed, formatRoomCreated, formatSendResult, formatTranscript, formatWho, invocation } from './format.ts';

export interface CliIo {
  stdout: (s: string) => void;
  stderr: (s: string) => void;
  /** Only PARTY_RUN is read from here. Defaults to process.env. */
  env?: Record<string, string | undefined>;
  /** System boundaries, replaced in tests. */
  deps?: Partial<Omit<StationDeps, 'run' | 'command'>> & { pid?: number };
}

const USAGE = `usage (every command needs --run <run-dir>, or PARTY_RUN; there is no default):
  party init   --run <run> [--awake-window-sec 600] [--heartbeat-sec 5] [--stale-sec 15]
  party join   --run <run> --agent <id> --platform <claude|codex|other> --session <native-id>
  party who    --run <run> [--agent <id>]
  party send   --run <run> --from <id> --to <id|all> --intent <question|answer|finding|handoff|fyi|ack> --text <text> [--re <msg-id>]
  party read   --run <run> --agent <id>
  party wait   --run <run> --agent <id> [--timeout-sec 86400]
  party listen --run <run> --agent <id> [--timeout-sec 86400]
  party listen --run <run> --agent <id> --check
  party stop   --run <run> --agent <id>
  party close  --run <run>
  party log    --run <run> [--agent <id>]
the booth's state lives in <run>/_party/; init needs an existing run directory
exit codes: 0 ok / message received / listen: messages waiting, run the printed read command / --check nothing to do,
  1 unexpected error, 2 usage error or refused,
  3 wait/listen timeout, 4 should not listen (member stopped or room closed), 5 --check: action needed (run the printed command),
  6 listen found a running listener: do not start another listen, keep going with the current work
`;

class UsageError extends Error {}

interface CommandOptions {
  required: string[];
  optional: string[];
}

const COMMANDS: Record<string, CommandOptions> = {
  init: { required: [], optional: ['awake-window-sec', 'heartbeat-sec', 'stale-sec'] },
  close: { required: [], optional: [] },
  stop: { required: ['agent'], optional: [] },
  join: { required: ['agent', 'platform', 'session'], optional: [] },
  who: { required: [], optional: ['agent'] },
  send: { required: ['from', 'to', 'intent', 'text'], optional: ['re'] },
  read: { required: ['agent'], optional: [] },
  wait: { required: ['agent'], optional: ['timeout-sec'] },
  listen: { required: ['agent'], optional: ['timeout-sec', 'check'] },
  log: { required: [], optional: ['agent'] },
};

/** Options that take no value. */
const FLAGS = new Set(['check']);

function parse(argv: string[]): { positional: string[]; options: Map<string, string> } {
  const positional: string[] = [];
  const options = new Map<string, string>();
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i] as string;
    if (!a.startsWith('--')) {
      positional.push(a);
      continue;
    }
    const eq = a.indexOf('=');
    let key: string;
    let value: string | undefined;
    if (FLAGS.has(a.slice(2))) {
      key = a.slice(2);
      value = 'true';
    } else if (eq > 0) {
      key = a.slice(2, eq);
      if (FLAGS.has(key)) throw new UsageError(`--${key} takes no value`);
      value = a.slice(eq + 1);
    } else {
      key = a.slice(2);
      value = argv[++i];
    }
    if (value === undefined) throw new UsageError(`missing value for --${key}`);
    if (options.has(key)) throw new UsageError(`--${key} given twice`);
    options.set(key, value);
  }
  return { positional, options };
}

function intOption(options: Map<string, string>, key: string): number | undefined {
  const v = options.get(key);
  if (v === undefined) return undefined;
  if (!/^\d+$/.test(v)) throw new UsageError(`--${key} must be a whole number`);
  return Number(v);
}

function quote(s: string): string {
  return /[\s"]/.test(s) ? `"${s}"` : s;
}

interface Ctx { io: CliIo; room: string; agent: string; inv: (verb: string) => string }

/** Prints a wait/listen result and returns its exit code. */
function report(res: WaitResult, verb: 'wait' | 'listen', timeoutSec: number, ctx: Ctx): number {
  const { io, room, agent, inv } = ctx;
  switch (res.outcome) {
    case 'delivered':
      io.stdout(formatDelivery(res.messages, { room, agent, inv }));
      return 0;
    case 'timeout':
      io.stdout(`[party] ${verb} timeout after ${timeoutSec}s; no message for ${agent}\n`
        + `[party] re-listen: ${inv(verb)} --agent ${agent} --timeout-sec ${timeoutSec}\n`);
      return 3;
    case 'stopped':
      io.stdout(`[party] stop listening: ${agent} is stopped in room ${room} (join again with the same details to resume)\n`);
      return 4;
    case 'closed':
      io.stdout(`[party] stop listening: room ${room} is closed\n`);
      return 4;
  }
}

export async function run(argv: string[], io: CliIo): Promise<number> {
  try {
    const { positional, options } = parse(argv);
    const [name, ...extra] = positional;
    if (name === undefined) throw new UsageError('missing command');
    if (name === 'help') {
      io.stdout(USAGE);
      return 0;
    }
    const spec = COMMANDS[name];
    if (!spec) throw new UsageError(`unknown command "${name}"`);
    if (extra.length > 0) throw new UsageError(`${name} takes no positional arguments (got "${extra.join(' ')}"); the booth is chosen with --run`);
    const env = io.env ?? process.env;
    const runArg = options.get('run') ?? env.PARTY_RUN;
    options.delete('run');
    if (runArg === undefined || runArg === '') throw new UsageError('--run <run-dir> (or PARTY_RUN) is required; there is no default booth');
    for (const key of options.keys()) {
      if (!spec.required.includes(key) && !spec.optional.includes(key)) throw new UsageError(`unknown option --${key} for ${name}`);
    }
    for (const key of spec.required) {
      if (!options.has(key)) throw new UsageError(`${name} needs --${key}`);
    }
    const runDir = path.resolve(runArg);
    const command = `node ${quote(fileURLToPath(import.meta.url).replaceAll('\\', '/'))}`;
    const deps: StationDeps = { ...io.deps, run: runDir, command };
    const inv = (verb: string) => invocation(command, runDir, verb);
    const opt = (key: string) => options.get(key) as string;

    if (name === 'init') {
      const info = initBooth(deps, {
        awakeWindowSec: intOption(options, 'awake-window-sec'),
        heartbeatSec: intOption(options, 'heartbeat-sec'),
        staleSec: intOption(options, 'stale-sec'),
      });
      io.stdout(formatRoomCreated(info));
      return 0;
    }
    const room = openBooth(deps);
    const roomName = room.info().name;
    switch (name) {
      case 'close': {
        io.stdout(formatRoomClosed(room.close()));
        return 0;
      }
      case 'listen': {
        const agent = opt('agent');
        if (options.has('check')) {
          if (options.has('timeout-sec')) throw new UsageError('--check does not wait, so it takes no --timeout-sec');
          const c = await room.check(agent);
          if (!c.needsAction) {
            io.stdout(`[party] check: no action needed (${c.reason})\n`);
            return 0;
          }
          io.stdout(`[party] check: action needed (${c.reason === 'pending' ? 'messages are waiting' : 'not listening'}); run:\n`
            + `${inv(c.reason === 'pending' ? 'read' : 'listen')} --agent ${agent}\n`);
          return 5;
        }
        const timeoutSec = intOption(options, 'timeout-sec') ?? DEFAULT_WAIT_TIMEOUT_SEC;
        const res = await room.listen(agent, { timeoutSec, pid: io.deps?.pid ?? process.pid });
        if (res.outcome === 'already_listening') {
          io.stdout(`[party] already listening (exit 6): ${agent} has an active listener in room ${roomName}\n`
            + '[party] 已有收聽中的 listen；不要再啟動背景 listen，繼續目前的工作\n');
          return 6;
        }
        if (res.outcome === 'notified') {
          io.stdout(formatNotice(res.pending ?? 0, { agent, inv }));
          return 0;
        }
        return report({ outcome: res.outcome, messages: res.messages }, 'listen', timeoutSec, { io, room: roomName, agent, inv });
      }
      case 'stop': {
        const agent = opt('agent');
        room.stop(agent);
        io.stdout(`[party] ${agent} stopped listening in room ${roomName}; its wait/listen ends within one heartbeat (join again with the same details to resume)\n`);
        return 0;
      }
      case 'join': {
        const { member, notice } = room.joinWithNotice({ agent: opt('agent'), platform: opt('platform'), session: opt('session') });
        io.stdout(formatJoined(roomName, member) + (notice ? `[party] notice: ${notice}\n` : ''));
        return 0;
      }
      case 'who': {
        if (options.has('agent')) room.touch(opt('agent'), 'who');
        io.stdout(formatWho(room.info(), room.who()));
        return 0;
      }
      case 'send': {
        const res = room.send({
          from: opt('from'), to: opt('to'), intent: opt('intent'), text: opt('text'), re: options.get('re') ?? null,
        });
        io.stdout(formatSendResult(res, path.join(runDir, '_inbox.md')));
        return 0;
      }
      case 'read': {
        const agent = opt('agent');
        const messages = room.take(agent, 'read');
        io.stdout(messages.length === 0 ? '[party] no new messages\n' : formatDelivery(messages, { room: roomName, agent, inv }));
        return 0;
      }
      case 'log': {
        if (options.has('agent')) room.touch(opt('agent'), 'log');
        io.stdout(formatTranscript(roomName, room.transcript()));
        return 0;
      }
      case 'wait': {
        const agent = opt('agent');
        const timeoutSec = intOption(options, 'timeout-sec') ?? DEFAULT_WAIT_TIMEOUT_SEC;
        const res = await room.wait(agent, { timeoutSec, pid: io.deps?.pid ?? process.pid });
        return report(res, 'wait', timeoutSec, { io, room: roomName, agent, inv });
      }
    }
    throw new UsageError(`unknown command "${name}"`);
  } catch (e) {
    if (e instanceof UsageError) {
      io.stderr(`[party] usage error: ${e.message}\n${USAGE}`);
      return 2;
    }
    if (e instanceof PartyError) {
      io.stderr(`[party] refused: ${e.message}\n`);
      return 2;
    }
    io.stderr(`[party] unexpected error: ${e instanceof Error ? e.message : String(e)}\n`);
    return 1;
  }
}

if (import.meta.main) process.exitCode = await run(process.argv.slice(2), { stdout: (s) => process.stdout.write(s), stderr: (s) => process.stderr.write(s) });
