export type PieceStatus =
  | 'backlog'
  | 'learning'
  | 'memorized'
  | 'maintaining'
  | 'performance-ready'
  | 'archived'

export const PIECE_STATUSES: PieceStatus[] = [
  'backlog',
  'learning',
  'memorized',
  'maintaining',
  'performance-ready',
  'archived',
]

export type PieceDifficulty = 'beginner' | 'intermediate' | 'advanced' | 'expert'

export const PIECE_DIFFICULTIES: PieceDifficulty[] = [
  'beginner',
  'intermediate',
  'advanced',
  'expert',
]

export interface Piece {
  id: number
  title: string
  composer: string | null
  key: string | null
  tempo_bpm: number | null
  difficulty: PieceDifficulty | null
  instrument: string | null
  goal_text: string | null
  goal_target_date: string | null
  status: PieceStatus
  tags: string[]
  is_favorite: boolean
  created_at: string
  updated_at: string
}

export interface PieceCreateInput {
  title: string
  composer?: string | null
  key?: string | null
  tempo_bpm?: number | null
  difficulty?: PieceDifficulty | null
  instrument?: string | null
  goal_text?: string | null
  goal_target_date?: string | null
  status?: PieceStatus
  tags?: string[]
  is_favorite?: boolean
}

export interface PieceUpdateInput {
  title?: string
  composer?: string | null
  key?: string | null
  tempo_bpm?: number | null
  difficulty?: PieceDifficulty | null
  instrument?: string | null
  goal_text?: string | null
  goal_target_date?: string | null
  status?: PieceStatus
  tags?: string[]
  is_favorite?: boolean
}

export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch('/api/health')
  if (!response.ok) throw new Error(`health check failed: ${response.status}`)
  return response.json()
}

export async function listPieces(
  filters?: {
    status?: PieceStatus
    favorite?: boolean
    difficulty?: PieceDifficulty
    instrument?: string
    inFocus?: boolean
  },
): Promise<Piece[]> {
  const params = new URLSearchParams()
  if (filters?.status) params.set('status', filters.status)
  if (filters?.favorite) params.set('favorite', 'true')
  if (filters?.difficulty) params.set('difficulty', filters.difficulty)
  if (filters?.instrument) params.set('instrument', filters.instrument)
  if (filters?.inFocus) params.set('in_focus', 'true')
  const query = params.toString()
  const response = await fetch(`/api/pieces${query ? `?${query}` : ''}`)
  if (!response.ok) throw new Error(`failed to list pieces: ${response.status}`)
  return response.json()
}

async function describeError(prefix: string, response: Response): Promise<string> {
  let detail = ''
  try {
    const body = await response.json()
    if (typeof body?.detail === 'string') {
      detail = body.detail
    } else if (Array.isArray(body?.detail)) {
      detail = body.detail
        .map((e: { msg?: string }) => e.msg)
        .filter(Boolean)
        .join('; ')
    }
  } catch {
    // response body wasn't JSON — fall back to status code below
  }
  return detail ? `${prefix}: ${detail} (${response.status})` : `${prefix}: ${response.status}`
}

export async function createPiece(input: PieceCreateInput): Promise<Piece> {
  const response = await fetch('/api/pieces', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) throw new Error(await describeError('failed to create piece', response))
  return response.json()
}

export async function updatePiece(id: number, input: PieceUpdateInput): Promise<Piece> {
  const response = await fetch(`/api/pieces/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) throw new Error(await describeError('failed to update piece', response))
  return response.json()
}

export async function deletePiece(id: number): Promise<void> {
  const response = await fetch(`/api/pieces/${id}`, { method: 'DELETE' })
  if (!response.ok) throw new Error(await describeError('failed to delete piece', response))
}

export interface PracticeSession {
  id: number
  piece_id: number
  practiced_at: string
  duration_minutes: number
  notes: string | null
  rating: number | null
  section: string | null
  created_at: string
  updated_at: string
}

export interface PracticeSessionCreateInput {
  piece_id: number
  practiced_at: string
  duration_minutes: number
  notes?: string | null
  rating?: number | null
  section?: string | null
}

export async function listPracticeSessions(
  filters?: { piece_id?: number },
): Promise<PracticeSession[]> {
  const params = new URLSearchParams()
  if (filters?.piece_id) params.set('piece_id', String(filters.piece_id))
  const query = params.toString()
  const response = await fetch(`/api/practice-sessions${query ? `?${query}` : ''}`)
  if (!response.ok) throw new Error(`failed to list practice sessions: ${response.status}`)
  return response.json()
}

export async function createPracticeSession(
  input: PracticeSessionCreateInput,
): Promise<PracticeSession> {
  const response = await fetch('/api/practice-sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    throw new Error(await describeError('failed to create practice session', response))
  }
  return response.json()
}

export interface SectionPracticeStats {
  section: string
  total_minutes: number
}

export interface PiecePracticeStats {
  piece_id: number
  piece_title: string
  total_minutes: number
  session_count: number
  last_practiced_at: string
  sections: SectionPracticeStats[]
}

export interface RecentlyPracticedPiece {
  piece_id: number
  piece_title: string
  last_practiced_at: string
}

export interface NeglectedPiece {
  piece_id: number
  piece_title: string
  last_practiced_at: string | null
}

export interface PracticeStats {
  total_minutes: number
  pieces: PiecePracticeStats[]
  recently_practiced: RecentlyPracticedPiece[]
  neglected: NeglectedPiece[]
  current_streak_days: number
  longest_streak_days: number
  minutes_this_week: number
  minutes_this_month: number
}

export async function getPracticeStats(): Promise<PracticeStats> {
  const response = await fetch('/api/practice-sessions/stats')
  if (!response.ok) throw new Error(`failed to load practice stats: ${response.status}`)
  return response.json()
}

export interface PracticeGoal {
  id: number
  target_minutes: number
  minutes_this_week: number
  created_at: string
  updated_at: string
}

export interface PracticeGoalSetInput {
  target_minutes: number
}

export async function getPracticeGoal(): Promise<PracticeGoal | null> {
  const response = await fetch('/api/practice-goal')
  if (!response.ok) throw new Error(`failed to load practice goal: ${response.status}`)
  return response.json()
}

export async function setPracticeGoal(input: PracticeGoalSetInput): Promise<PracticeGoal> {
  const response = await fetch('/api/practice-goal', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) throw new Error(await describeError('failed to set practice goal', response))
  return response.json()
}

export type SheetResourceKind = 'url' | 'physical' | 'local-doc'

export const SHEET_RESOURCE_KINDS: SheetResourceKind[] = ['url', 'physical', 'local-doc']

export interface SheetResource {
  id: number
  piece_id: number
  kind: SheetResourceKind
  reference: string
  label: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface SheetResourceCreateInput {
  piece_id: number
  kind: SheetResourceKind
  reference: string
  label?: string | null
  notes?: string | null
}

export async function listSheetResources(
  filters?: { piece_id?: number },
): Promise<SheetResource[]> {
  const params = new URLSearchParams()
  if (filters?.piece_id) params.set('piece_id', String(filters.piece_id))
  const query = params.toString()
  const response = await fetch(`/api/sheet-resources${query ? `?${query}` : ''}`)
  if (!response.ok) throw new Error(`failed to list sheet resources: ${response.status}`)
  return response.json()
}

export async function createSheetResource(
  input: SheetResourceCreateInput,
): Promise<SheetResource> {
  const response = await fetch('/api/sheet-resources', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    throw new Error(await describeError('failed to create sheet resource', response))
  }
  return response.json()
}

export async function deleteSheetResource(id: number): Promise<void> {
  const response = await fetch(`/api/sheet-resources/${id}`, { method: 'DELETE' })
  if (!response.ok) {
    throw new Error(await describeError('failed to delete sheet resource', response))
  }
}

export interface RepertoireList {
  id: number
  name: string
  created_at: string
  updated_at: string
  piece_count: number
}

export interface RepertoireListDetail {
  id: number
  name: string
  created_at: string
  updated_at: string
  pieces: Piece[]
}

export interface RepertoireListCreateInput {
  name: string
}

export interface RepertoireListUpdateInput {
  name?: string
}

export async function listRepertoireLists(): Promise<RepertoireList[]> {
  const response = await fetch('/api/repertoire-lists')
  if (!response.ok) throw new Error(`failed to list repertoire lists: ${response.status}`)
  return response.json()
}

export async function getRepertoireList(id: number): Promise<RepertoireListDetail> {
  const response = await fetch(`/api/repertoire-lists/${id}`)
  if (!response.ok) throw new Error(`failed to load repertoire list: ${response.status}`)
  return response.json()
}

export async function createRepertoireList(
  input: RepertoireListCreateInput,
): Promise<RepertoireList> {
  const response = await fetch('/api/repertoire-lists', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    throw new Error(await describeError('failed to create repertoire list', response))
  }
  return response.json()
}

export async function updateRepertoireList(
  id: number,
  input: RepertoireListUpdateInput,
): Promise<RepertoireList> {
  const response = await fetch(`/api/repertoire-lists/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    throw new Error(await describeError('failed to update repertoire list', response))
  }
  return response.json()
}

export async function deleteRepertoireList(id: number): Promise<void> {
  const response = await fetch(`/api/repertoire-lists/${id}`, { method: 'DELETE' })
  if (!response.ok) {
    throw new Error(await describeError('failed to delete repertoire list', response))
  }
}

export async function addPieceToRepertoireList(
  listId: number,
  pieceId: number,
): Promise<RepertoireListDetail> {
  const response = await fetch(`/api/repertoire-lists/${listId}/pieces`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ piece_id: pieceId }),
  })
  if (!response.ok) {
    throw new Error(await describeError('failed to add piece to repertoire list', response))
  }
  return response.json()
}

export async function removePieceFromRepertoireList(
  listId: number,
  pieceId: number,
): Promise<void> {
  const response = await fetch(`/api/repertoire-lists/${listId}/pieces/${pieceId}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error(await describeError('failed to remove piece from repertoire list', response))
  }
}
