<script lang="ts">
  import { onMount } from 'svelte'
  import {
    getHealth,
    getPracticeGoal,
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
    type PracticeGoal,
    type PracticeSession,
    type PracticeStats,
    type RepertoireList,
    type SheetResource,
  } from './lib/api'
  import Modal from './lib/Modal.svelte'
  import PieceForm from './lib/PieceForm.svelte'
  import PieceList from './lib/PieceList.svelte'
  import PracticeGoalForm from './lib/PracticeGoalForm.svelte'
  import PracticeSessionForm from './lib/PracticeSessionForm.svelte'
  import PracticeSessionList from './lib/PracticeSessionList.svelte'
  import PracticeStatsView from './lib/PracticeStats.svelte'
  import RepertoireListForm from './lib/RepertoireListForm.svelte'
  import RepertoireListList from './lib/RepertoireListList.svelte'
  import RotationPlanner from './lib/RotationPlanner.svelte'
  import SectionHeader from './lib/SectionHeader.svelte'
  import SheetResourceForm from './lib/SheetResourceForm.svelte'
  import SheetResourceList from './lib/SheetResourceList.svelte'

  let health = $state<string>('checking...')
  let pieces = $state<Piece[]>([])
  let error = $state<string | null>(null)
  let statusFilter = $state<PieceStatus | ''>('')
  let favoritesOnly = $state<boolean>(false)
  let difficultyFilter = $state<PieceDifficulty | ''>('')
  let editingPiece = $state<Piece | null>(null)
  let pieceModalOpen = $state(false)
  let sessions = $state<PracticeSession[]>([])
  let sessionModalOpen = $state(false)
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
  let goal = $state<PracticeGoal | null>(null)
  let goalModalOpen = $state(false)
  let sheetResources = $state<SheetResource[]>([])
  let resourceModalOpen = $state(false)
  let repertoireLists = $state<RepertoireList[]>([])
  let editingRepertoireList = $state<RepertoireList | null>(null)
  let listModalOpen = $state(false)
  let focusPieces = $state<Piece[]>([])

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

  async function refreshGoal(): Promise<void> {
    goal = await getPracticeGoal()
  }

  async function refreshSheetResources(): Promise<void> {
    sheetResources = await listSheetResources()
  }

  async function refreshRepertoireLists(): Promise<void> {
    repertoireLists = await listRepertoireLists()
  }

  async function refreshFocusPieces(): Promise<void> {
    focusPieces = await listPieces({ inFocus: true })
  }

  onMount(async () => {
    try {
      const healthResult = await getHealth()
      health = healthResult.status
      await refreshPieces()
      await refreshSessions()
      await refreshStats()
      await refreshGoal()
      await refreshSheetResources()
      await refreshRepertoireLists()
      await refreshFocusPieces()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  })

  function openAddPiece(): void {
    editingPiece = null
    pieceModalOpen = true
  }

  function openEditPiece(piece: Piece): void {
    editingPiece = piece
    pieceModalOpen = true
  }

  function closePieceModal(): void {
    pieceModalOpen = false
    editingPiece = null
  }

  async function handleSessionSaved(saved: PracticeSession): Promise<void> {
    sessions = [...sessions, saved].sort((a, b) => b.practiced_at.localeCompare(a.practiced_at))
    sessionModalOpen = false
    try {
      await refreshStats()
      await refreshGoal()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  }

  function handleGoalSaved(saved: PracticeGoal): void {
    goal = saved
    goalModalOpen = false
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
    pieceModalOpen = false
    editingPiece = null
    refreshFocusPieces().catch((err) => {
      error = err instanceof Error ? err.message : String(err)
    })
  }

  function handlePieceDeleted(id: number): void {
    pieces = pieces.filter((p) => p.id !== id)
    if (editingPiece?.id === id) closePieceModal()
    sheetResources = sheetResources.filter((r) => r.piece_id !== id)
    refreshRepertoireLists().catch((err) => {
      error = err instanceof Error ? err.message : String(err)
    })
    refreshFocusPieces().catch((err) => {
      error = err instanceof Error ? err.message : String(err)
    })
  }

  function handleSheetResourceSaved(saved: SheetResource): void {
    sheetResources = [saved, ...sheetResources]
    resourceModalOpen = false
  }

  function handleSheetResourceDeleted(id: number): void {
    sheetResources = sheetResources.filter((r) => r.id !== id)
  }

  function openAddList(): void {
    editingRepertoireList = null
    listModalOpen = true
  }

  function closeListModal(): void {
    listModalOpen = false
    editingRepertoireList = null
  }

  function handleRepertoireListSaved(saved: RepertoireList): void {
    const exists = repertoireLists.some((l) => l.id === saved.id)
    repertoireLists = exists
      ? repertoireLists.map((l) => (l.id === saved.id ? saved : l))
      : [...repertoireLists, saved]
    listModalOpen = false
    editingRepertoireList = null
  }

  function handleRepertoireListDeleted(id: number): void {
    repertoireLists = repertoireLists.filter((l) => l.id !== id)
    if (editingRepertoireList?.id === id) closeListModal()
  }

  function handleRepertoireListCountChanged(id: number, pieceCount: number): void {
    repertoireLists = repertoireLists.map((l) => (l.id === id ? { ...l, piece_count: pieceCount } : l))
  }
</script>

<div class="page">
  <header class="masthead">
    <h1>Music Repertoire</h1>
    <span class="chip" class:chip-accent={health === 'ok'}>API — {health}</span>
  </header>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <main>
    <section class="panel">
      <SectionHeader eyebrow="Repertoire" title="Pieces">
        {#snippet right()}
          <div class="filters">
            <label class="filter">
              Status
              <select bind:value={statusFilter} onchange={onStatusFilterChange}>
                <option value="">All</option>
                {#each PIECE_STATUSES as status (status)}
                  <option value={status}>{status}</option>
                {/each}
              </select>
            </label>
            <label class="filter">
              Difficulty
              <select bind:value={difficultyFilter} onchange={onStatusFilterChange}>
                <option value="">All</option>
                {#each PIECE_DIFFICULTIES as d (d)}
                  <option value={d}>{d}</option>
                {/each}
              </select>
            </label>
            <label class="filter checkbox">
              <input type="checkbox" bind:checked={favoritesOnly} onchange={onStatusFilterChange} />
              Favorites only
            </label>
          </div>
          <button type="button" onclick={openAddPiece}>+ Add piece</button>
        {/snippet}
      </SectionHeader>

      <PieceList {pieces} onEdit={openEditPiece} onDeleted={handlePieceDeleted} onUpdated={handlePieceSaved} />
    </section>

    <section class="panel">
      <SectionHeader eyebrow="Repertoire" title="Currently in Focus" />
      <RotationPlanner pieces={focusPieces} />
    </section>

    <section class="panel">
      <SectionHeader eyebrow="Practice" title="Sessions">
        {#snippet right()}
          <button type="button" onclick={() => (sessionModalOpen = true)}>+ Log session</button>
        {/snippet}
      </SectionHeader>
      <PracticeSessionList {sessions} {pieces} />
    </section>

    <section class="panel">
      <SectionHeader eyebrow="Practice" title="Statistics">
        {#snippet right()}
          <button type="button" class="secondary" onclick={() => (goalModalOpen = true)}>
            {goal ? 'Edit goal' : 'Set goal'}
          </button>
        {/snippet}
      </SectionHeader>
      <PracticeStatsView {stats} {goal} />
    </section>

    <section class="panel">
      <SectionHeader eyebrow="Repertoire" title="Sheet Music Resources">
        {#snippet right()}
          <button type="button" onclick={() => (resourceModalOpen = true)}>+ Add resource</button>
        {/snippet}
      </SectionHeader>
      <SheetResourceList resources={sheetResources} {pieces} onDeleted={handleSheetResourceDeleted} />
    </section>

    <section class="panel">
      <SectionHeader eyebrow="Repertoire" title="Lists">
        {#snippet right()}
          <button type="button" onclick={openAddList}>+ New list</button>
        {/snippet}
      </SectionHeader>
      <RepertoireListList
        lists={repertoireLists}
        {pieces}
        onEdit={(l) => {
          editingRepertoireList = l
          listModalOpen = true
        }}
        onDeleted={handleRepertoireListDeleted}
        onCountChanged={handleRepertoireListCountChanged}
      />
    </section>
  </main>
</div>

<Modal open={pieceModalOpen} title={editingPiece ? 'Edit piece' : 'Add piece'} onClose={closePieceModal}>
  <PieceForm piece={editingPiece} onSaved={handlePieceSaved} onCancel={closePieceModal} />
</Modal>

<Modal open={sessionModalOpen} title="Log practice session" onClose={() => (sessionModalOpen = false)}>
  <PracticeSessionForm {pieces} onSaved={handleSessionSaved} onCancel={() => (sessionModalOpen = false)} />
</Modal>

<Modal open={goalModalOpen} title={goal ? 'Edit weekly goal' : 'Set weekly goal'} onClose={() => (goalModalOpen = false)}>
  <PracticeGoalForm {goal} onSaved={handleGoalSaved} onCancel={() => (goalModalOpen = false)} />
</Modal>

<Modal open={resourceModalOpen} title="Add sheet resource" onClose={() => (resourceModalOpen = false)}>
  <SheetResourceForm {pieces} onSaved={handleSheetResourceSaved} onCancel={() => (resourceModalOpen = false)} />
</Modal>

<Modal open={listModalOpen} title={editingRepertoireList ? 'Rename list' : 'New repertoire list'} onClose={closeListModal}>
  <RepertoireListForm list={editingRepertoireList} onSaved={handleRepertoireListSaved} onCancel={closeListModal} />
</Modal>

<style>
  .page {
    max-width: 44rem;
    margin: 0 auto;
    padding: var(--space-6) var(--space-4) var(--space-7);
  }
  .masthead {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
    margin-bottom: var(--space-6);
  }
  .filters {
    display: flex;
    align-items: end;
    gap: var(--space-4);
  }
  .filter {
    font-size: var(--text-xs);
  }
  .filter select {
    padding: var(--space-1) var(--space-2);
    font-size: var(--text-sm);
  }
  .filter.checkbox {
    flex-direction: row;
    align-items: center;
    gap: var(--space-1);
  }
  main {
    display: flex;
    flex-direction: column;
  }
</style>
