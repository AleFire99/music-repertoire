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
  let goal = $state<PracticeGoal | null>(null)
  let sheetResources = $state<SheetResource[]>([])
  let repertoireLists = $state<RepertoireList[]>([])
  let editingRepertoireList = $state<RepertoireList | null>(null)
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

  async function handleSessionSaved(saved: PracticeSession): Promise<void> {
    sessions = [...sessions, saved].sort((a, b) => b.practiced_at.localeCompare(a.practiced_at))
    try {
      await refreshStats()
      await refreshGoal()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  }

  function handleGoalSaved(saved: PracticeGoal): void {
    goal = saved
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
    refreshFocusPieces().catch((err) => {
      error = err instanceof Error ? err.message : String(err)
    })
  }

  function handlePieceDeleted(id: number): void {
    pieces = pieces.filter((p) => p.id !== id)
    if (editingPiece?.id === id) editingPiece = null
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

<div class="page">
  <header class="masthead">
    <div>
      <h1>Music Repertoire</h1>
      <p class="tagline">a practice journal</p>
    </div>
    <span class="chip chip-quiet health" class:health-ok={health === 'ok'}>
      API — {health}
    </span>
  </header>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <main>
    <section class="sheet">
      <SectionHeader title={editingPiece ? 'Edit Piece' : 'Add Piece'} />
      <PieceForm
        piece={editingPiece}
        onSaved={handlePieceSaved}
        onCancel={() => (editingPiece = null)}
      />
    </section>

    <section class="sheet">
      <SectionHeader title="Pieces">
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
        {/snippet}
      </SectionHeader>

      <PieceList
        {pieces}
        onEdit={(p) => (editingPiece = p)}
        onDeleted={handlePieceDeleted}
        onUpdated={handlePieceSaved}
      />
    </section>

    <section class="sheet">
      <SectionHeader title="Currently in Focus" />
      <RotationPlanner pieces={focusPieces} />
    </section>

    <section class="sheet">
      <SectionHeader title="Log Practice Session" />
      <PracticeSessionForm {pieces} onSaved={handleSessionSaved} />
    </section>

    <section class="sheet">
      <SectionHeader title="Recent Sessions" />
      <PracticeSessionList {sessions} {pieces} />
    </section>

    <section class="sheet">
      <SectionHeader title="Weekly Practice Goal" />
      <PracticeGoalForm {goal} onSaved={handleGoalSaved} />
    </section>

    <section class="sheet">
      <SectionHeader title="Practice Statistics" />
      <PracticeStatsView {stats} {goal} />
    </section>

    <section class="sheet">
      <SectionHeader title="Sheet Music Resources" />
      <SheetResourceForm {pieces} onSaved={handleSheetResourceSaved} />
      <SheetResourceList resources={sheetResources} {pieces} onDeleted={handleSheetResourceDeleted} />
    </section>

    <section class="sheet">
      <SectionHeader title={editingRepertoireList ? 'Rename List' : 'Add Repertoire List'} />
      <RepertoireListForm
        list={editingRepertoireList}
        onSaved={handleRepertoireListSaved}
        onCancel={() => (editingRepertoireList = null)}
      />
    </section>

    <section class="sheet">
      <SectionHeader title="Repertoire Lists" />
      <RepertoireListList
        lists={repertoireLists}
        {pieces}
        onEdit={(l) => (editingRepertoireList = l)}
        onDeleted={handleRepertoireListDeleted}
        onCountChanged={handleRepertoireListCountChanged}
      />
    </section>
  </main>
</div>

<style>
  .page {
    max-width: 44rem;
    margin: 0 auto;
    padding: var(--space-6) var(--space-4) var(--space-7);
  }
  .masthead {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--space-4);
    margin-bottom: var(--space-6);
  }
  .tagline {
    margin: var(--space-1) 0 0;
    font-style: italic;
    font-variant-caps: all-small-caps;
    letter-spacing: 0.04em;
    color: var(--ink-soft);
  }
  .health {
    flex: none;
    margin-left: 0;
  }
  .health-ok {
    color: var(--accent-strong);
  }
  .filters {
    display: flex;
    align-items: end;
    gap: var(--space-4);
    font-family: var(--font-body);
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
