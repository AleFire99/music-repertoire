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
