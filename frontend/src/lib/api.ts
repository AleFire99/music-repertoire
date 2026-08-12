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

export interface Piece {
  id: number
  title: string
  composer: string | null
  status: PieceStatus
  tags: string[]
  created_at: string
  updated_at: string
}

export interface PieceCreateInput {
  title: string
  composer?: string | null
  status?: PieceStatus
  tags?: string[]
}

export interface PieceUpdateInput {
  title?: string
  composer?: string | null
  status?: PieceStatus
  tags?: string[]
}

export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch('/api/health')
  if (!response.ok) throw new Error(`health check failed: ${response.status}`)
  return response.json()
}

export async function listPieces(filters?: { status?: PieceStatus }): Promise<Piece[]> {
  const params = new URLSearchParams()
  if (filters?.status) params.set('status', filters.status)
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
