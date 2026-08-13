<script lang="ts">
  import { onMount } from 'svelte'
  import {
    getHealth,
    getPracticeStats,
    listPieces,
    listPracticeSessions,
    listRepertoireLists,
    listSheetResources,
    PIECE_STATUSES,
    PIECE_DIFFICULTIES,
    type Piece,
    type PieceStatus,
    type PieceDifficulty,
    type PracticeSession,
    type PracticeStats,
    type RepertoireList,
    type SheetResource,
  } from './lib/api'
  import PieceForm from './lib/PieceForm.svelte'
  import PieceList from './lib/PieceList.svelte'
  import PracticeSessionForm from './lib/PracticeSessionForm.svelte'
  import PracticeSessionList from './lib/PracticeSessionList.svelte'
  import PracticeStatsView from './lib/PracticeStats.svelte'
  import RepertoireListForm from './lib/RepertoireListForm.svelte'
  import RepertoireListList from './lib/RepertoireListList.svelte'
  import SheetResourceForm from './lib/SheetResourceForm.svelte'
  import SheetResourceList from './lib/SheetResourceList.svelte'

  let health = $state<string>('checking...')
  let pieces = $state<Piece[]>([])
  let error = $state<string | null>(null)
  let statusFilter = $state<PieceStatus | ''>('')
  let favoritesOnly = $state<boolean>(false)
  let difficultyFilter = $state<PieceDifficulty | ''>('')
  let editingPiece = $state<Piece | null>(null)
  let sessions = $state<PracticeSession[]>([])
  let stats = $state<PracticeStats>({
    total_minutes: 0,
    pieces: [],
    recently_practiced: [],
    neglected: [],
    current_streak_days: 0,
    longest_streak_days: 0,
    minutes_this_week: 0,
    minutes_this_month: 0,
  })
  let sheetResources = $state<SheetResource[]>([])
  let repertoireLists = $state<RepertoireList[]>([])
  let editingRepertoireList = $state<RepertoireList | null>(null)

  async function refreshPieces(): Promise<void> {
    pieces = await listPieces({
      status: statusFilter || undefined,
      favorite: favoritesOnly || undefined,
      difficulty: difficultyFilter || undefined,
    })
  }

  async function refreshSessions(): Promise<void> {
    sessions = await listPracticeSessions()
  }

  async function refreshStats(): Promise<void> {
    stats = await getPracticeStats()
  }

  async function refreshSheetResources(): Promise<void> {
    sheetResources = await listSheetResources()
  }

  async function refreshRepertoireLists(): Promise<void> {
    repertoireLists = await listRepertoireLists()
  }

  onMount(async () => {
    try {
      const healthResult = await getHealth()
      health = healthResult.status
      await refreshPieces()
      await refreshSessions()
      await refreshStats()
      await refreshSheetResources()
      await refreshRepertoireLists()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  })

  async function handleSessionSaved(saved: PracticeSession): Promise<void> {
    sessions = [...sessions, saved].sort((a, b) => b.practiced_at.localeCompare(a.practiced_at))
    try {
      await refreshStats()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
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
    sheetResources = sheetResources.filter((r) => r.piece_id !== id)
    refreshRepertoireLists().catch((err) => {
      error = err instanceof Error ? err.message : String(err)
    })
  }

  function handleSheetResourceSaved(saved: SheetResource): void {
    sheetResources = [saved, ...sheetResources]
  }

  function handleSheetResourceDeleted(id: number): void {
    sheetResources = sheetResources.filter((r) => r.id !== id)
  }

  function handleRepertoireListSaved(saved: RepertoireList): void {
    const exists = repertoireLists.some((l) => l.id === saved.id)
    repertoireLists = exists
      ? repertoireLists.map((l) => (l.id === saved.id ? saved : l))
      : [...repertoireLists, saved]
    editingRepertoireList = null
  }

  function handleRepertoireListDeleted(id: number): void {
    repertoireLists = repertoireLists.filter((l) => l.id !== id)
    if (editingRepertoireList?.id === id) editingRepertoireList = null
  }

  function handleRepertoireListCountChanged(id: number, pieceCount: number): void {
    repertoireLists = repertoireLists.map((l) => (l.id === id ? { ...l, piece_count: pieceCount } : l))
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
  <label>
    <input type="checkbox" bind:checked={favoritesOnly} onchange={onStatusFilterChange} />
    Favorites only
  </label>
  <label>
    Filter by difficulty:
    <select bind:value={difficultyFilter} onchange={onStatusFilterChange}>
      <option value="">All</option>
      {#each PIECE_DIFFICULTIES as d (d)}
        <option value={d}>{d}</option>
      {/each}
    </select>
  </label>

  <PieceList
    {pieces}
    onEdit={(p) => (editingPiece = p)}
    onDeleted={handlePieceDeleted}
    onUpdated={handlePieceSaved}
  />

  <h2>Log Practice Session</h2>
  <PracticeSessionForm {pieces} onSaved={handleSessionSaved} />

  <h2>Recent Sessions</h2>
  <PracticeSessionList {sessions} {pieces} />

  <h2>Practice Statistics</h2>
  <PracticeStatsView {stats} />

  <h2>Sheet Music Resources</h2>
  <SheetResourceForm {pieces} onSaved={handleSheetResourceSaved} />
  <SheetResourceList resources={sheetResources} {pieces} onDeleted={handleSheetResourceDeleted} />

  <h2>{editingRepertoireList ? 'Rename List' : 'Add Repertoire List'}</h2>
  <RepertoireListForm
    list={editingRepertoireList}
    onSaved={handleRepertoireListSaved}
    onCancel={() => (editingRepertoireList = null)}
  />

  <h2>Repertoire Lists</h2>
  <RepertoireListList
    lists={repertoireLists}
    {pieces}
    onEdit={(l) => (editingRepertoireList = l)}
    onDeleted={handleRepertoireListDeleted}
    onCountChanged={handleRepertoireListCountChanged}
  />
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
