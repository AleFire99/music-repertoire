<script lang="ts">
  import { onMount } from 'svelte'
  import {
    getHealth,
    listPieces,
    listPracticeSessions,
    PIECE_STATUSES,
    type Piece,
    type PieceStatus,
    type PracticeSession,
  } from './lib/api'
  import PieceForm from './lib/PieceForm.svelte'
  import PieceList from './lib/PieceList.svelte'
  import PracticeSessionForm from './lib/PracticeSessionForm.svelte'
  import PracticeSessionList from './lib/PracticeSessionList.svelte'

  let health = $state<string>('checking...')
  let pieces = $state<Piece[]>([])
  let error = $state<string | null>(null)
  let statusFilter = $state<PieceStatus | ''>('')
  let editingPiece = $state<Piece | null>(null)
  let sessions = $state<PracticeSession[]>([])

  async function refreshPieces(): Promise<void> {
    pieces = await listPieces({ status: statusFilter || undefined })
  }

  async function refreshSessions(): Promise<void> {
    sessions = await listPracticeSessions()
  }

  onMount(async () => {
    try {
      const healthResult = await getHealth()
      health = healthResult.status
      await refreshPieces()
      await refreshSessions()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  })

  function handleSessionSaved(saved: PracticeSession): void {
    sessions = [...sessions, saved].sort((a, b) => b.practiced_at.localeCompare(a.practiced_at))
  }

  async function onStatusFilterChange(): Promise<void> {
    try {
      await refreshPieces()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  }

  function handlePieceSaved(saved: Piece): void {
    const exists = pieces.some((p) => p.id === saved.id)
    pieces = exists ? pieces.map((p) => (p.id === saved.id ? saved : p)) : [...pieces, saved]
    editingPiece = null
  }

  function handlePieceDeleted(id: number): void {
    pieces = pieces.filter((p) => p.id !== id)
    if (editingPiece?.id === id) editingPiece = null
  }
</script>

<main>
  <h1>Music Repertoire</h1>
  <p>API health: <strong>{health}</strong></p>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <h2>{editingPiece ? 'Edit Piece' : 'Add Piece'}</h2>
  <PieceForm
    piece={editingPiece}
    onSaved={handlePieceSaved}
    onCancel={() => (editingPiece = null)}
  />

  <h2>Pieces</h2>
  <label>
    Filter by status:
    <select bind:value={statusFilter} onchange={onStatusFilterChange}>
      <option value="">All</option>
      {#each PIECE_STATUSES as status (status)}
        <option value={status}>{status}</option>
      {/each}
    </select>
  </label>

  <PieceList {pieces} onEdit={(p) => (editingPiece = p)} onDeleted={handlePieceDeleted} />

  <h2>Log Practice Session</h2>
  <PracticeSessionForm {pieces} onSaved={handleSessionSaved} />

  <h2>Recent Sessions</h2>
  <PracticeSessionList {sessions} {pieces} />
</main>

<style>
  main {
    max-width: 32rem;
    margin: 2rem auto;
    font-family: system-ui, sans-serif;
  }
  .error {
    color: #b00020;
  }
</style>
