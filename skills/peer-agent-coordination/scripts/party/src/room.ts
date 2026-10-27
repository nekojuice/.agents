// Discussion booth core: a booth is a run directory; its state lives in <run>/_party/.
// Roster, messages, single delivery, transcript data, listeners. No platform state is read.
import fs from 'node:fs';
import path from 'node:path';
import { randomBytes } from 'node:crypto';
import { invocation } from './format.ts';

/** System boundaries injected by callers (tests replace them). */
export interface StationDeps {
  /** The run directory that is this booth; station state lives in <run>/_party/. */
  run: string;
  now?: () => Date;
  /** How agents invoke this tool, used in printed commands. Default `party`. */
  command?: string;
  /** Waits between polls during `wait`. */
  sleep?: (ms: number) => Promise<void>;
  /** Creates a file only if it does not exist yet (throws EEXIST otherwise); used to claim a delivery. */
  createExclusive?: (file: string) => void;
  /** Deletes a file if present (missing is fine); used for listener cleanup and for rolling back a failed send. */
  removeFile?: (file: string) => void;
}

/** A request the station refuses (bad input, unknown member, closed room...). */
export class PartyError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'PartyError';
  }
}

export interface RoomInfo {
  name: string;
  createdAt: string;
  awakeWindowSec: number;
  /** A waiting listener refreshes its record's lastBeat this often. */
  heartbeatSec: number;
  /** A listener whose lastBeat is older than this no longer counts as listening. */
  staleSec: number;
  /** When the room was closed (irreversible), or null while it is open. */
  closedAt: string | null;
}

export interface CreateRoomOptions {
  awakeWindowSec?: number;
  heartbeatSec?: number;
  staleSec?: number;
}

/** How a wait or listen ended. */
export type WaitOutcome = 'delivered' | 'timeout' | 'stopped' | 'closed';

export interface WaitResult {
  outcome: WaitOutcome;
  messages: Message[];
}

/** A valid listener record: its id and its last heartbeat in epoch ms. */
interface LiveListener {
  listenerId: string;
  lastBeat: number;
}

/**
 * How a listen ended. A listen never delivers: 'notified' means `pending` messages are
 * waiting and the agent takes them with `read`; `messages` is always empty.
 */
export interface ListenResult {
  outcome: Exclude<WaitOutcome, 'delivered'> | 'notified' | 'already_listening';
  messages: Message[];
  /** Only with 'notified': how many messages are waiting. */
  pending?: number;
}

/** A waiting listener's record: listeners/<member>/<listenerId>.json. */
interface ListenerRecord {
  listenerId: string;
  startedAt: string;
  timeoutSec: number;
  lastBeat: string;
  /** For people reading the file only; never used to decide anything. */
  pid?: number;
}

export const PLATFORMS = ['claude', 'codex', 'other'] as const;
export type Platform = (typeof PLATFORMS)[number];
export const INTENTS = ['question', 'answer', 'finding', 'handoff', 'fyi', 'ack'] as const;
export type Intent = (typeof INTENTS)[number];
/** Intents that end an exchange; replies to them are refused (loop protection). */
export const TERMINAL_INTENTS: readonly Intent[] = ['ack', 'fyi'];

export type Participation = 'active' | 'stopped';

export interface Member {
  id: string;
  platform: Platform;
  session: string;
  joinedAt: string;
  /** stopped: the member no longer listens (`party stop`); an identical rejoin makes it active. */
  participation: Participation;
}

export interface JoinInput {
  agent: string;
  platform: string;
  session: string;
}

export interface SendInput {
  from: string;
  /** A member id, or `all` for every member except the sender. */
  to: string;
  intent: string;
  text: string;
  re?: string | null;
}

export type TakeVia = 'read' | 'wait';

export interface Message {
  id: string;
  /** 1-based position in the room, assigned under the room lock; defines delivery order. */
  seq: number;
  from: string;
  /** As addressed: a member id or `all`. */
  to: string;
  recipients: string[];
  intent: Intent;
  re: string | null;
  sentAt: string;
  text: string;
}

export type WakeAction = 'none' | 'ask_user' | 'native_or_ask_user' | 'stopped';

export interface RecipientStatus {
  member: string;
  /** Where the recipient is (platform and native session); the text shown to people is built in format.ts. */
  platform: Platform;
  session: string;
  listening: boolean;
  /**
   * none: the recipient is listening. ask_user: cross-platform (or `other`) and not
   * listening; give the user the relay notice. native_or_ask_user: same platform and not
   * listening; remind it with your own platform's means or give the user the relay notice.
   * stopped: the recipient ran `party stop`; nobody should wake it.
   */
  action: WakeAction;
  readCommand: string;
}

export const PRESENCE_ACTIONS = ['join', 'send', 'read', 'wait_start', 'delivered', 'notified', 'timeout', 'log', 'who', 'stop'] as const;
export type PresenceAction = (typeof PRESENCE_ACTIONS)[number];
export type MemberState = 'listening' | 'awake' | 'offline';

export interface MemberPresence {
  member: Member;
  /** Inferred from tool actions, not from the platform's real turn state. */
  state: MemberState;
  lastAction: PresenceAction;
  lastAt: string;
}

export interface TranscriptEntry {
  message: Message;
  delivery: { member: string; delivered: boolean }[];
  /** Ids of later messages whose `re` points at this one. */
  replies: string[];
}

export interface SendResult {
  message: Message;
  recipients: RecipientStatus[];
}

export const DEFAULT_AWAKE_WINDOW_SEC = 600;
export const DEFAULT_HEARTBEAT_SEC = 5;
export const DEFAULT_STALE_SEC = 15;
const LISTENER_FILE = /^([0-9a-f]{16})\.json$/;
const AGENT_ID = /^[a-z0-9-]{1,40}$/;
const MESSAGE_ID = /^[A-Za-z0-9-]{1,80}$/;
const LOCK_TIMEOUT_MS = 5000;
/** Intents that expect a reply; they are marked relay: pending when the user must carry a notice. */
const RELAY_INTENTS: readonly Intent[] = ['question', 'handoff', 'finding'];

interface Resolved {
  run: string;
  now: () => Date;
  command: string;
  sleep: (ms: number) => Promise<void>;
  createExclusive: (file: string) => void;
  removeFile: (file: string) => void;
}

function resolve(deps: StationDeps): Resolved {
  return {
    run: path.resolve(deps.run),
    now: deps.now ?? (() => new Date()),
    command: deps.command ?? 'party',
    sleep: deps.sleep ?? ((ms) => new Promise((r) => setTimeout(r, ms))),
    createExclusive: deps.createExclusive ?? ((file) => fs.closeSync(fs.openSync(file, 'wx'))),
    removeFile: deps.removeFile ?? ((file) => fs.rmSync(file, { force: true })),
  };
}

function positiveInt(value: number, label: string): number {
  if (!Number.isInteger(value) || value < 1) throw new PartyError(`${label} must be a positive integer`);
  return value;
}

export const DEFAULT_WAIT_TIMEOUT_SEC = 86400;
const POLL_MS = 1000;
export const MAX_WAIT_TIMEOUT_SEC = 86400;

function checkTimeout(sec: number): void {
  if (!Number.isInteger(sec) || sec < 1 || sec > MAX_WAIT_TIMEOUT_SEC) {
    throw new PartyError(`timeout must be a whole number of seconds from 1 to ${MAX_WAIT_TIMEOUT_SEC}`);
  }
}

/**
 * Lenient reader of the skill roster <run>/_agents.md (a Markdown table with at least a
 * handle column). Never writes it. ok=false when the file exists but no such table is found.
 */
export function agentsTable(run: string): { exists: boolean; ok: boolean; rows: Array<Record<string, string>> } {
  const file = path.join(run, '_agents.md');
  let text: string;
  try {
    text = fs.readFileSync(file, 'utf8');
  } catch {
    return { exists: false, ok: true, rows: [] };
  }
  const cells = (line: string) => line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim().replace(/^`|`$/g, ''));
  const lines = text.split(/\r?\n/).filter((l) => l.trim().startsWith('|'));
  const headerAt = lines.findIndex((l) => cells(l).includes('handle'));
  if (headerAt < 0) return { exists: true, ok: false, rows: [] };
  const header = cells(lines[headerAt] as string);
  const rows = lines.slice(headerAt + 1)
    .filter((l) => !/^[\s|:-]+$/.test(l))
    .map((l) => Object.fromEntries(cells(l).map((c, i) => [header[i] ?? String(i), c])));
  return { exists: true, ok: true, rows };
}

/** The run directory must already exist: the station never creates a run. */
function existingRun(run: string): void {
  let ok = false;
  try {
    ok = fs.statSync(run).isDirectory();
  } catch {
    ok = false;
  }
  if (!ok) throw new PartyError(`run directory not found: ${run} (the station does not create runs)`);
}

const BOOTH_DIR = '_party';

/** The title line of a run's _inbox.md (skill §7 shape). */
function inboxTitle(run: string): string {
  return `# Inbox — ${path.basename(run)} (append-only)\n`;
}

// ---------- small file helpers ----------

function sleepSync(ms: number): void {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

const RETRYABLE = new Set(['EPERM', 'EACCES', 'EBUSY']);

/** rename with a short retry for transient Windows locks (antivirus, indexers). */
function renameRetry(src: string, dst: string): void {
  for (let attempt = 0; ; attempt++) {
    try {
      fs.renameSync(src, dst);
      return;
    } catch (e) {
      const code = (e as NodeJS.ErrnoException).code ?? '';
      if (!RETRYABLE.has(code) || attempt >= 5) throw e;
      sleepSync(20);
    }
  }
}

/**
 * Claims one pending message for delivery. The delivered marker is created with an
 * exclusive create ('wx'), which only one process can win; the pending marker is
 * removed afterwards. A plain rename is not used as the claim because on Windows two
 * processes renaming the same file can both report success (observed in tests).
 * Returns false when another reader already claimed it.
 */
function claim(pendingMarker: string, deliveredMarker: string, createExclusive: (file: string) => void): boolean {
  let won = false;
  for (let attempt = 0; ; attempt++) {
    try {
      createExclusive(deliveredMarker);
      won = true;
      break;
    } catch (e) {
      const code = (e as NodeJS.ErrnoException).code ?? '';
      if (code === 'EEXIST') break;
      if (!RETRYABLE.has(code) || attempt >= 5) throw e;
      sleepSync(20);
    }
  }
  // Best effort: a leftover pending marker is harmless because its delivered marker exists.
  try {
    fs.rmSync(pendingMarker, { force: true });
  } catch {
    // another reader is removing the same marker
  }
  return won;
}

let tmpCounter = 0;
function writeJsonAtomic(file: string, value: unknown): void {
  const tmp = `${file}.${process.pid}.${++tmpCounter}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(value, null, 2) + '\n');
  renameRetry(tmp, file);
}

function readJson<T>(file: string): T {
  return JSON.parse(fs.readFileSync(file, 'utf8')) as T;
}

// ---------- booths ----------

/**
 * Creates the booth of an existing run: <run>/_party/ (refused if it already exists) and,
 * when missing, <run>/_inbox.md holding only its title.
 */
export function initBooth(deps: StationDeps, opts: CreateRoomOptions = {}): RoomInfo {
  const d = resolve(deps);
  const name = path.basename(d.run);
  const info: RoomInfo = {
    name,
    createdAt: d.now().toISOString(),
    awakeWindowSec: positiveInt(opts.awakeWindowSec ?? DEFAULT_AWAKE_WINDOW_SEC, 'awake window seconds'),
    heartbeatSec: positiveInt(opts.heartbeatSec ?? DEFAULT_HEARTBEAT_SEC, 'heartbeat seconds'),
    staleSec: positiveInt(opts.staleSec ?? DEFAULT_STALE_SEC, 'stale seconds'),
    closedAt: null,
  };
  if (info.staleSec <= 2 * info.heartbeatSec) {
    throw new PartyError(`stale seconds (${info.staleSec}) must be more than twice the heartbeat seconds (${info.heartbeatSec})`);
  }
  existingRun(d.run);
  const dir = path.join(d.run, BOOTH_DIR);
  try {
    fs.mkdirSync(dir); // claims the booth atomically
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === 'EEXIST') throw new PartyError(`a booth already exists in ${d.run}`);
    throw e;
  }
  fs.mkdirSync(path.join(dir, 'messages'));
  writeJsonAtomic(path.join(dir, 'roster.json'), []);
  writeJsonAtomic(path.join(dir, 'room.json'), info);
  try {
    fs.writeFileSync(path.join(d.run, '_inbox.md'), inboxTitle(d.run), { flag: 'wx' });
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code !== 'EEXIST') throw e;
  }
  return info;
}

export function openBooth(deps: StationDeps): Room {
  const d = resolve(deps);
  existingRun(d.run);
  const dir = path.join(d.run, BOOTH_DIR);
  if (!fs.existsSync(path.join(dir, 'room.json'))) throw new PartyError(`no booth in ${d.run}; run init first`);
  return new Room(d, dir);
}

export class Room {
  #d: Resolved;
  #dir: string;

  /** Use openBooth() instead of constructing directly. */
  constructor(d: Resolved, dir: string) {
    this.#d = d;
    this.#dir = dir;
  }

  info(): RoomInfo {
    const raw = readJson<Partial<RoomInfo> & { name: string; createdAt: string }>(path.join(this.#dir, 'room.json'));
    return {
      name: raw.name,
      createdAt: raw.createdAt,
      awakeWindowSec: raw.awakeWindowSec ?? DEFAULT_AWAKE_WINDOW_SEC,
      heartbeatSec: raw.heartbeatSec ?? DEFAULT_HEARTBEAT_SEC,
      staleSec: raw.staleSec ?? DEFAULT_STALE_SEC,
      closedAt: raw.closedAt ?? null,
    };
  }

  roster(): Member[] {
    return readJson<Array<Omit<Member, 'participation'> & { participation?: Participation }>>(path.join(this.#dir, 'roster.json'))
      .map((m) => ({ ...m, participation: m.participation ?? 'active' }));
  }

  /** Marks `agent` as no longer listening; its waits end within one heartbeat. */
  stop(agent: string): void {
    this.#member(agent);
    this.#locked(() => {
      const roster = this.roster().map((m) => (m.id === agent ? { ...m, participation: 'stopped' as const } : m));
      writeJsonAtomic(path.join(this.#dir, 'roster.json'), roster);
    });
    this.#recordBestEffort(agent, 'stop');
  }

  /**
   * Closes the room (irreversible; closing again keeps the first time). Afterwards send
   * and join are refused and every wait or listen ends within one heartbeat.
   */
  close(): RoomInfo {
    return this.#locked(() => {
      const raw = readJson<Record<string, unknown>>(path.join(this.#dir, 'room.json'));
      if (!raw.closedAt) writeJsonAtomic(path.join(this.#dir, 'room.json'), { ...raw, closedAt: this.#d.now().toISOString() });
      return this.info();
    });
  }

  #closedError(): PartyError {
    return new PartyError(`room "${this.info().name}" is closed`);
  }

  join(input: JoinInput): Member {
    return this.joinWithNotice(input).member;
  }

  /**
   * Joins and also checks the skill roster <run>/_agents.md (read only): a row with the same
   * handle but another canonical_id refuses the join; a missing row or an unreadable file
   * only yields a notice for the roster owner.
   */
  joinWithNotice(input: JoinInput): { member: Member; notice: string | null } {
    const { agent, platform, session } = input;
    if (!AGENT_ID.test(agent) || agent === 'all') throw new PartyError(`invalid agent id "${agent}": use 1-40 characters of a-z, 0-9 and - (not "all")`);
    if (!(PLATFORMS as readonly string[]).includes(platform)) throw new PartyError(`invalid platform "${platform}": use ${PLATFORMS.join(', ')}`);
    if (!session.trim() || session.length > 200 || /[\r\n]/.test(session)) throw new PartyError('session id must be a non-empty single line of at most 200 characters');
    let notice: string | null = null;
    const agents = agentsTable(this.#d.run);
    if (agents.exists && !agents.ok) {
      notice = '無法解析 _agents.md 的名冊表格，未比對；請 owner 確認名冊';
    } else if (agents.exists) {
      const row = agents.rows.find((r) => r.handle === agent);
      if (!row) notice = `_agents.md 尚未列出此成員，請 owner 補登（handle ${agent}）`;
      else if (row.canonical_id !== undefined && row.canonical_id !== session) {
        throw new PartyError(`_agents.md lists handle "${agent}" with canonical_id ${row.canonical_id}, not ${session}; pick another agent id or ask the roster owner`);
      }
    }
    const member = this.#joinRoster(agent, platform, session);
    return { member, notice };
  }

  #joinRoster(agent: string, platform: string, session: string): Member {
    const joined = this.#locked(() => {
      if (this.info().closedAt) throw this.#closedError();
      const roster = this.roster();
      const existing = roster.find((m) => m.id === agent);
      if (existing) {
        if (existing.platform !== platform || existing.session !== session) {
          throw new PartyError(`agent "${agent}" already joined as ${existing.platform} session ${existing.session}; pick another agent id`);
        }
        if (existing.participation === 'active') return existing;
        const resumed: Member = { ...existing, participation: 'active' };
        writeJsonAtomic(path.join(this.#dir, 'roster.json'), roster.map((m) => (m.id === agent ? resumed : m)));
        return resumed;
      }
      const member: Member = { id: agent, platform: platform as Platform, session, joinedAt: this.#d.now().toISOString(), participation: 'active' };
      writeJsonAtomic(path.join(this.#dir, 'roster.json'), [...roster, member]);
      return member;
    });
    this.#recordBestEffort(agent, 'join');
    return joined;
  }

  send(input: SendInput): SendResult {
    const { from, to, intent, text } = input;
    const re = input.re ?? null;
    this.#member(from);
    if (to !== 'all') this.#member(to);
    if (!(INTENTS as readonly string[]).includes(intent)) throw new PartyError(`invalid intent "${intent}": use ${INTENTS.join(', ')}`);
    if (!text.trim()) throw new PartyError('message text is empty');
    if (re !== null && !MESSAGE_ID.test(re)) throw new PartyError(`invalid --re "${re}"`);

    const result = this.#locked((): SendResult => {
      if (this.info().closedAt) throw this.#closedError();
      const ids = this.#messageIds();
      if (re !== null) {
        if (!ids.includes(re)) throw new PartyError(`--re ${re}: no such message in this room`);
        const target = this.#message(re);
        if (TERMINAL_INTENTS.includes(target.intent)) {
          throw new PartyError(`message ${re} is "${target.intent}", which ends the exchange and cannot be replied to`);
        }
      }
      const roster = this.roster();
      const sender = roster.find((x) => x.id === from) as Member;
      const recipients = to === 'all' ? roster.filter((m) => m.id !== from).map((m) => m.id) : [to];
      const statuses = recipients.map((id) => this.#recipientStatus(roster.find((x) => x.id === id) as Member, sender));

      // Id: <UTC seconds, ISO 8601 basic>-<seq>; seq counts up per booth and skips ids
      // already used here or in _inbox.md (e.g. written there by hand). Only headers at the
      // start of a line count; an escaped body line or an id mid-line does not.
      const inboxFile = path.join(this.#d.run, '_inbox.md');
      const inboxText = fs.existsSync(inboxFile) ? fs.readFileSync(inboxFile, 'utf8') : null;
      const taken = new Set([...ids, ...[...(inboxText ?? '').matchAll(/^\[id: ([^\s|\]]+) \|/gm)].map((x) => x[1] as string)]);
      const stamp = this.#d.now().toISOString().replace(/\.\d+Z$/, 'Z').replace(/[-:]/g, '');
      let seq = Math.max(0, ...ids.map((x) => this.#message(x).seq)) + 1;
      while (taken.has(`${stamp}-${String(seq).padStart(2, '0')}`)) seq++;
      const id = `${stamp}-${String(seq).padStart(2, '0')}`;
      const msg: Message = {
        id, seq, from, to, recipients,
        intent: intent as Intent, re, sentAt: this.#d.now().toISOString(), text,
      };
      const relayPending = RELAY_INTENTS.includes(msg.intent)
        && statuses.some((st) => st.action === 'ask_user' || st.action === 'native_or_ask_user');

      // Order: station copy -> _inbox.md entry -> pending markers. If the inbox entry
      // cannot be written, the station copy is removed and nothing is queued.
      const copy = path.join(this.#dir, 'messages', `${id}.json`);
      writeJsonAtomic(copy, msg);
      try {
        this.#appendInbox(inboxFile, inboxText, msg, relayPending);
      } catch (e) {
        try {
          this.#d.removeFile(copy);
        } catch {
          // the original error is the one to report
        }
        throw e;
      }
      // If any marker fails, the markers made so far and the station copy are removed (best
      // effort) so that nobody receives the message; the _inbox.md entry stays (append-only).
      const made: string[] = [];
      try {
        for (const r of recipients) {
          const dir = path.join(this.#dir, 'pending', r);
          fs.mkdirSync(dir, { recursive: true });
          const marker = path.join(dir, id);
          fs.writeFileSync(marker, '');
          made.push(marker);
        }
      } catch (e) {
        for (const file of [...made, copy]) {
          try {
            this.#d.removeFile(file);
          } catch {
            // the original error is the one to report
          }
        }
        throw e;
      }
      return { message: msg, recipients: statuses };
    });
    this.#recordBestEffort(from, 'send');
    for (const r of result.recipients) this.pruneListeners(r.member);
    return result;
  }

  #recipientStatus(m: Member, sender: Member): RecipientStatus {
    const listening = this.isListening(m.id);
    const samePlatform = m.platform === sender.platform && m.platform !== 'other';
    const action: WakeAction = m.participation === 'stopped' ? 'stopped' : listening ? 'none' : samePlatform ? 'native_or_ask_user' : 'ask_user';
    const readCommand = `${invocation(this.#d.command, this.#d.run, 'read')} --agent ${m.id}`;
    return { member: m.id, platform: m.platform, session: m.session, listening, action, readCommand };
  }

  /**
   * Appends one skill-format entry ([id: … | from: … | to: … | intent: … | re: …] + text) to
   * _inbox.md. A body line starting with "[id: " gets a leading backslash so it cannot pose
   * as another entry; the station copy keeps the original text.
   */
  #appendInbox(file: string, current: string | null, m: Message, relayPending: boolean): void {
    let prefix: string;
    if (current === null) {
      fs.writeFileSync(file, inboxTitle(this.#d.run), { flag: 'wx' });
      prefix = '\n';
    } else {
      prefix = current.endsWith('\n\n') ? '' : current.endsWith('\n') ? '\n' : '\n\n';
    }
    const agents = agentsTable(this.#d.run);
    const label = (id: string) => {
      const row = agents.rows.find((r) => r.handle === id);
      return row?.display_id ? `${id}#${row.display_id}` : id;
    };
    const header = `[id: ${m.id} | from: ${label(m.from)} | to: ${m.to === 'all' ? 'all' : label(m.to)} | intent: ${m.intent} | re: ${m.re ?? '-'}${relayPending ? ' | relay: pending' : ''}]`;
    const body = m.text.split('\n').map((line) => (line.startsWith('[id: ') ? `\\${line}` : line)).join('\n');
    fs.appendFileSync(file, `${prefix}${header}\n${body}${body.endsWith('\n') ? '' : '\n'}`);
  }

  /**
   * Registers a listener record for `agent` (validates the timeout first) and returns its
   * random listener id. `pid` is stored for people only; listening is judged by heartbeat.
   */
  startListening(agent: string, opts: { timeoutSec: number; pid?: number }): string {
    return this.#register(agent, opts).listenerId;
  }

  #register(agent: string, opts: { timeoutSec: number; pid?: number }): ListenerRecord {
    this.#member(agent);
    checkTimeout(opts.timeoutSec);
    const listenerId = randomBytes(8).toString('hex');
    const now = this.#d.now().toISOString();
    const rec: ListenerRecord = { listenerId, startedAt: now, timeoutSec: opts.timeoutSec, lastBeat: now };
    if (opts.pid !== undefined) rec.pid = opts.pid;
    const dir = path.join(this.#dir, 'listeners', agent);
    fs.mkdirSync(dir, { recursive: true });
    writeJsonAtomic(path.join(dir, `${listenerId}.json`), rec);
    // Presence is best effort: a failure here must neither fail the listen nor leave a
    // record with no process behind it.
    this.#recordBestEffort(agent, 'wait_start');
    return rec;
  }

  /**
   * Blocks until at least one message is pending for `agent` (all pending are delivered,
   * in order) or the timeout passes. The listener record's lastBeat is refreshed every
   * heartbeatSec while waiting; a failed heartbeat write is retried at the next poll.
   */
  async wait(agent: string, opts: { timeoutSec: number; pid?: number }): Promise<WaitResult> {
    this.#member(agent);
    checkTimeout(opts.timeoutSec);
    const ended = this.#shouldNotListen(agent);
    if (ended) return { outcome: ended, messages: [] };
    return this.#waitLoop(agent, this.#register(agent, opts), () => {
      const messages = this.take(agent, 'wait');
      return messages.length > 0 ? { outcome: 'delivered', messages } : null;
    });
  }

  /**
   * Ensures `agent` is listening, in this order: stopped or closed → that outcome;
   * a confirmed live listener already exists → 'already_listening' (the CLI exits 6);
   * messages are pending → report how many and return (no waiting); otherwise register and
   * wait like `wait`, ending with the same notice when a message arrives. A listen never
   * delivers: the messages stay pending until `read` (or `wait`) takes them. The check and the registration happen under the room lock, so of
   * several concurrent listens for one member at most one goes on to wait.
   */
  async listen(agent: string, opts: { timeoutSec: number; pid?: number }): Promise<ListenResult> {
    this.#member(agent);
    checkTimeout(opts.timeoutSec);
    const unconfirmed = new Set<string>();
    for (;;) {
      const step = this.#locked((): ListenResult | ListenerRecord | { confirm: LiveListener } => {
        const ended = this.#shouldNotListen(agent);
        if (ended) return { outcome: ended, messages: [] };
        const live = this.#freshestListener(agent, unconfirmed);
        if (live) return this.#beatIsRecent(live) ? { outcome: 'already_listening', messages: [] } : { confirm: live };
        const notice = this.#notice(agent);
        if (notice) return notice;
        return this.#register(agent, opts);
      });
      if ('confirm' in step) {
        if (await this.#confirmBeat(agent, step.confirm)) return { outcome: 'already_listening', messages: [] };
        unconfirmed.add(step.confirm.listenerId);
        continue;
      }
      if ('outcome' in step) return step;
      return this.#waitLoop(agent, step, () => this.#notice(agent));
    }
  }

  /**
   * A 'notified' result when `agent` has pending messages, otherwise null. Delivers nothing;
   * a notice is recorded as the presence action 'notified' (best effort).
   */
  #notice(agent: string): ListenResult | null {
    const pending = this.pendingCount(agent);
    if (pending === 0) return null;
    this.#recordBestEffort(agent, 'notified');
    return { outcome: 'notified', messages: [], pending };
  }

  /**
   * Does `agent` need to act to stay reachable? Delivers nothing and registers nothing.
   * Fine (no action) when stopped, closed, or confirmed listening with nothing pending;
   * otherwise an action is needed (run `listen`). Only the heartbeat confirmation may
   * wait, for at most about heartbeatSec + 2 seconds.
   */
  async check(agent: string): Promise<{ needsAction: boolean; reason: 'stopped' | 'closed' | 'listening' | 'not_listening' | 'pending' }> {
    this.#member(agent);
    const ended = this.#shouldNotListen(agent);
    if (ended) return { needsAction: false, reason: ended };
    if (this.hasPending(agent)) return { needsAction: true, reason: 'pending' };
    const live = this.#freshestListener(agent, new Set());
    if (live && (this.#beatIsRecent(live) || await this.#confirmBeat(agent, live))) return { needsAction: false, reason: 'listening' };
    return { needsAction: true, reason: 'not_listening' };
  }

  /**
   * The valid listener record with the newest heartbeat, ignoring `skip` ids. A stopped
   * member never counts as listening; this is the only place that rule lives.
   */
  #freshestListener(agent: string, skip: Set<string>): LiveListener | null {
    if (this.roster().find((m) => m.id === agent)?.participation === 'stopped') return null;
    let best: LiveListener | null = null;
    for (const f of this.#listenerFiles(agent)) {
      if (!f.valid || skip.has(f.listenerId)) continue;
      if (!best || f.lastBeat > best.lastBeat) best = { listenerId: f.listenerId, lastBeat: f.lastBeat };
    }
    return best;
  }

  /** A heartbeat no older than heartbeatSec + 2 s needs no confirmation. */
  #beatIsRecent(live: LiveListener): boolean {
    return this.#d.now().getTime() - live.lastBeat <= (this.info().heartbeatSec + 2) * 1000;
  }

  /**
   * Waits until the listener's next expected heartbeat (plus 2 s slack, at most about
   * heartbeatSec + 2 s from now) and reports whether its lastBeat moved forward. A killed
   * listener inside staleSec does not move, so it is not mistaken for a live one.
   */
  async #confirmBeat(agent: string, live: LiveListener): Promise<boolean> {
    const hb = this.info().heartbeatSec * 1000;
    const now = this.#d.now().getTime();
    const beats = Math.max(1, Math.ceil((now - live.lastBeat - 2000) / hb));
    const target = live.lastBeat + beats * hb + 2000;
    await this.#d.sleep(Math.max(0, Math.min(target - now, hb + 2000)));
    const again = this.#listenerFiles(agent).find((f) => f.listenerId === live.listenerId);
    return again !== undefined && again.valid && again.lastBeat > live.lastBeat;
  }

  /** True when `agent` has messages that no wait/read has taken yet. */
  hasPending(agent: string): boolean {
    return this.pendingCount(agent) > 0;
  }

  /** How many messages for `agent` no wait/read has taken yet. */
  pendingCount(agent: string): number {
    const pendingDir = path.join(this.#dir, 'pending', agent);
    if (!fs.existsSync(pendingDir)) return 0;
    return fs.readdirSync(pendingDir).filter((id) => MESSAGE_ID.test(id)
      && !fs.existsSync(path.join(this.#dir, 'delivered', agent, id))
      && fs.existsSync(path.join(this.#dir, 'messages', `${id}.json`))).length;
  }

  /** 'closed' or 'stopped' when `agent` should not listen any more, otherwise null. */
  #shouldNotListen(agent: string): 'stopped' | 'closed' | null {
    if (this.info().closedAt) return 'closed';
    if (this.#member(agent).participation === 'stopped') return 'stopped';
    return null;
  }

  /**
   * The shared wait: polls `poll` until it returns a result, then ends with it; otherwise
   * keeps the heartbeat and ends on timeout, stop or close. The record is always removed.
   */
  async #waitLoop<R extends { outcome: string; messages: Message[] }>(agent: string, rec: ListenerRecord, poll: () => R | null): Promise<R | { outcome: 'timeout' | 'stopped' | 'closed'; messages: Message[] }> {
    const { heartbeatSec } = this.info();
    const file = path.join(this.#dir, 'listeners', agent, `${rec.listenerId}.json`);
    const started = Date.parse(rec.startedAt);
    const deadline = started + rec.timeoutSec * 1000;
    let lastBeat = started;
    try {
      for (;;) {
        const got = poll();
        if (got) return got;
        const now = this.#d.now().getTime();
        // Stop/close are checked at heartbeat cadence: still within one heartbeat interval,
        // without re-reading room.json and the roster on every poll.
        if (now - lastBeat >= heartbeatSec * 1000) {
          const ended = this.#shouldNotListen(agent);
          if (ended) return { outcome: ended, messages: [] };
        }
        if (now >= deadline) {
          this.#recordBestEffort(agent, 'timeout');
          return { outcome: 'timeout', messages: [] };
        }
        if (now - lastBeat >= heartbeatSec * 1000) {
          try {
            // Written from memory, so a record deleted meanwhile (pruned or removed by
            // hand) is rebuilt with the same id, start and timeout.
            fs.mkdirSync(path.dirname(file), { recursive: true });
            writeJsonAtomic(file, { ...rec, lastBeat: new Date(now).toISOString() });
            lastBeat = now;
          } catch {
            // retried at the next poll; if it keeps failing the listener goes stale (safe side)
          }
        }
        await this.#d.sleep(Math.min(POLL_MS, heartbeatSec * 1000, deadline - now));
      }
    } finally {
      this.stopListening(agent, rec.listenerId);
    }
  }

  /**
   * Best-effort removal of one listener record; never throws, so it cannot replace the
   * result of the wait that called it. A record left behind goes stale on its own.
   */
  stopListening(agent: string, listenerId: string): void {
    try {
      this.#d.removeFile(path.join(this.#dir, 'listeners', agent, `${listenerId}.json`));
    } catch {
      // stale after staleSec without heartbeats
    }
  }

  /**
   * True when `agent` has a valid listener record: its lastBeat is at most staleSec old and
   * now is before startedAt + timeoutSec. No PID or process state is consulted, so a
   * listener run by another OS account is judged the same way. A stopped member is never
   * listening (see #freshestListener). Read-only.
   */
  isListening(agent: string): boolean {
    return this.#freshestListener(agent, new Set()) !== null;
  }

  /**
   * Deletes invalid listener records (stale, past their timeout, old format, unreadable).
   * Best effort: a failed delete is ignored and never affects the calling command.
   */
  pruneListeners(agent: string): void {
    try {
      for (const f of this.#listenerFiles(agent)) {
        if (f.valid) continue;
        try {
          this.#d.removeFile(f.file);
        } catch {
          // another process may be deleting it, or it is locked; try again next time
        }
      }
    } catch {
      // listing failed; cleanup is optional
    }
  }

  #listenerFiles(agent: string): Array<{ file: string; valid: boolean; listenerId: string; lastBeat: number }> {
    const dir = path.join(this.#dir, 'listeners', agent);
    if (!fs.existsSync(dir)) return [];
    const { staleSec } = this.info();
    const now = this.#d.now().getTime();
    return fs.readdirSync(dir).filter((f) => !f.endsWith('.tmp')).map((f) => {
      const file = path.join(dir, f);
      const id = LISTENER_FILE.exec(f)?.[1];
      let rec: Partial<ListenerRecord> | null = null;
      try {
        if (id) rec = readJson<Partial<ListenerRecord>>(file);
      } catch {
        rec = null;
      }
      const beat = Date.parse(String(rec?.lastBeat));
      const start = Date.parse(String(rec?.startedAt));
      const valid = rec !== null && rec.listenerId === id && typeof rec.timeoutSec === 'number'
        && now - beat <= staleSec * 1000 && now < start + rec.timeoutSec * 1000;
      return { file, valid, listenerId: id ?? '', lastBeat: beat };
    });
  }

  /**
   * Every message in send order, with whether each recipient has taken it and which
   * later messages reply to it. Delivery is not processing: only a reply (`re`) shows that.
   */
  transcript(): TranscriptEntry[] {
    const messages = this.#messageIds().map((id) => this.#message(id)).sort((x, y) => x.seq - y.seq);
    return messages.map((message) => ({
      message,
      delivery: message.recipients.map((member) => ({
        member,
        delivered: fs.existsSync(path.join(this.#dir, 'delivered', member, message.id)),
      })),
      replies: messages.filter((m) => m.re === message.id).map((m) => m.id),
    }));
  }

  /** Records a member's last action (for commands such as log, who and a wait timeout). */
  touch(agent: string, action: PresenceAction): void {
    this.#member(agent);
    if (!(PRESENCE_ACTIONS as readonly string[]).includes(action)) throw new PartyError(`unknown action "${action}"`);
    this.#record(agent, action);
  }

  /**
   * Infers each member's state from tool actions only (never from platform state):
   * listening = a live listener record; awake = last action within the room's awake
   * window (inclusive); otherwise offline. Without a recorded action, joinedAt counts.
   */
  who(): MemberPresence[] {
    const windowMs = this.info().awakeWindowSec * 1000;
    const now = this.#d.now().getTime();
    return this.roster().map((member) => {
      const file = path.join(this.#dir, 'presence', `${member.id}.json`);
      const last = fs.existsSync(file)
        ? readJson<{ action: PresenceAction; at: string }>(file)
        : { action: 'join' as const, at: member.joinedAt };
      const state: MemberState = this.isListening(member.id)
        ? 'listening'
        : now - Date.parse(last.at) <= windowMs ? 'awake' : 'offline';
      return { member, state, lastAction: last.action, lastAt: last.at };
    });
  }

  /** Records presence, ignoring failures: presence only feeds the inferred state. */
  #recordBestEffort(agent: string, action: PresenceAction): void {
    try {
      this.#record(agent, action);
    } catch {
      // presence is an inference aid
    }
  }

  #record(agent: string, action: PresenceAction): void {
    const dir = path.join(this.#dir, 'presence');
    fs.mkdirSync(dir, { recursive: true });
    writeJsonAtomic(path.join(dir, `${agent}.json`), { action, at: this.#d.now().toISOString() });
  }

  #message(id: string): Message {
    return readJson<Message>(path.join(this.#dir, 'messages', `${id}.json`));
  }

  #messageIds(): string[] {
    return fs.readdirSync(path.join(this.#dir, 'messages'))
      .filter((f) => f.endsWith('.json'))
      .map((f) => f.slice(0, -'.json'.length));
  }

  /**
   * Delivers every pending message for `agent`, in send order. A message is claimed by
   * creating its delivered/<agent>/<id> marker with an exclusive create ('wx'): only one
   * caller can create it, so concurrent readers of the same member never receive a
   * message twice. Renaming pending/ into delivered/ is deliberately not used as the
   * claim: on Windows two processes renaming the same file can both report success,
   * which delivered the same message twice in tests.
   *
   * Every message claimed by this call is returned. If a claim fails, claiming stops
   * there (the rest stay pending, keeping send order) and the messages already claimed
   * are still returned; the error is raised only when nothing was claimed. Recording
   * presence is best effort and never loses a claimed message.
   */
  take(agent: string, via: TakeVia): Message[] {
    this.#member(agent);
    const got = this.#claimPending(agent);
    // A read is always an action; a wait poll only counts when it delivers something.
    // presence is an inference aid; the claimed messages must still reach the caller
    if (via === 'read') this.#recordBestEffort(agent, 'read');
    else if (got.length > 0) this.#recordBestEffort(agent, 'delivered');
    return got;
  }

  #claimPending(agent: string): Message[] {
    const pendingDir = path.join(this.#dir, 'pending', agent);
    if (!fs.existsSync(pendingDir)) return [];
    const queued = fs.readdirSync(pendingDir)
      .filter((id) => MESSAGE_ID.test(id) && fs.existsSync(path.join(this.#dir, 'messages', `${id}.json`)))
      .map((id) => this.#message(id))
      .sort((x, y) => x.seq - y.seq);
    if (queued.length === 0) return [];
    const deliveredDir = path.join(this.#dir, 'delivered', agent);
    fs.mkdirSync(deliveredDir, { recursive: true });
    const got: Message[] = [];
    for (const m of queued) {
      try {
        if (claim(path.join(pendingDir, m.id), path.join(deliveredDir, m.id), this.#d.createExclusive)) got.push(m);
      } catch (e) {
        if (got.length === 0) throw e;
        break; // return what is already claimed; the rest stays pending for the next take
      }
    }
    return got;
  }

  #member(id: string): Member {
    const found = this.roster().find((m) => m.id === id);
    if (!found) throw new PartyError(`agent "${id}" is not in room "${this.info().name}"; join first`);
    return found;
  }

  /** Serializes roster changes and message writes with an exclusive lock file. */
  #locked<T>(fn: () => T): T {
    const lock = path.join(this.#dir, 'roster.lock');
    const deadline = Date.now() + LOCK_TIMEOUT_MS;
    let fd: number | undefined;
    while (fd === undefined) {
      try {
        fd = fs.openSync(lock, 'wx');
      } catch (e) {
        const code = (e as NodeJS.ErrnoException).code ?? '';
        if (code !== 'EEXIST' && !RETRYABLE.has(code)) throw e;
        if (Date.now() > deadline) {
          throw new PartyError(`room is locked by ${lock}; if no party command is running, delete that file and retry`);
        }
        sleepSync(15);
      }
    }
    try {
      return fn();
    } finally {
      fs.closeSync(fd);
      fs.rmSync(lock, { force: true });
    }
  }
}
