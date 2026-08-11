export interface Piece {
  id: number
  title: string
  composer: string | null
  created_at: string
  updated_at: string
}

export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch('/api/health')
  if (!response.ok) throw new Error(`health check failed: ${response.status}`)
  return response.json()
}

export async function listPieces(): Promise<Piece[]> {
  const response = await fetch('/api/pieces')
  if (!response.ok) throw new Error(`failed to list pieces: ${response.status}`)
  return response.json()
}
