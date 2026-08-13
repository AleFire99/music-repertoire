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
  import Icon from './lib/Icon.svelte'
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

  type ViewId = 'pieces' | 'focus' | 'sessions' | 'stats' | 'resources' | 'lists'

  const NAV_ITEMS: { id: ViewId; label: string; icon: string }[] = [
    { id: 'pieces', label: 'Pieces', icon: 'piece' },
    { id: 'focus', label: 'Focus', icon: 'focus' },
    { id: 'sessions', label: 'Sessions', icon: 'session' },
    { id: 'stats', label: 'Statistics', icon: 'stats' },
    { id: 'resources', label: 'Resources', icon: 'resource' },
    { id: 'lists', label: 'Lists', icon: 'list' },
  ]

  let activeView = $state<ViewId>('pieces')
  let sidebarCollapsed = $state(localStorage.getItem('sidebar-collapsed') === 'true')

  function toggleSidebar(): void {
    sidebarCollapsed = !sidebarCollapsed
    localStorage.setItem('sidebar-collapsed', String(sidebarCollapsed))
  }

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

  function setStatusFilter(status: PieceStatus | ''): void {
    statusFilter = status
    onStatusFilterChange()
  }

  function setDifficultyFilter(difficulty: PieceDifficulty | ''): void {
    difficultyFilter = difficulty
    onStatusFilterChange()
  }

  function toggleFavoritesOnly(): void {
    favoritesOnly = !favoritesOnly
    onStatusFilterChange()
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

<div class="app-shell" class:collapsed={sidebarCollapsed}>
  <aside class="sidebar">
    <div class="masthead">
      <h1>Music Repertoire</h1>
      <p class="colophon caption">{pieces.length} piece{pieces.length === 1 ? '' : 's'} catalogued</p>
    </div>

    <nav>
      <ul>
        {#each NAV_ITEMS as item (item.id)}
          <li>
            <button
              type="button"
              class="nav-item"
              class:active={activeView === item.id}
              onclick={() => (activeView = item.id)}
              title={item.label}
            >
              <span class="tick" aria-hidden="true"></span>
              <Icon name={item.icon} />
              <span class="label">{item.label}</span>
            </button>
          </li>
        {/each}
      </ul>
    </nav>

    <div class="sidebar-footer">
      <button
        type="button"
        class="rail-toggle"
        onclick={toggleSidebar}
        aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        <Icon name="rail" size={16} />
      </button>
      <div class="health">
        <span class="dot" class:online={health === 'ok'} aria-hidden="true"></span>
        <span class="health-label caption">{health === 'ok' ? 'connected' : 'offline'}</span>
      </div>
    </div>
  </aside>

  <main class="content">
    {#if error}
      <p class="error">{error}</p>
    {/if}

    {#if activeView === 'pieces'}
      <SectionHeader
        title="Pieces"
        dek="Every piece in the repertoire, catalogued with its status, difficulty, and goal."
      >
        {#snippet actions()}
          <div class="filter-groups">
            <div class="filter-group">
              <span class="caption">Status</span>
              <span class="toggle-row">
                <button type="button" class="text-toggle" class:active={statusFilter === ''} onclick={() => setStatusFilter('')}>all</button>
                {#each PIECE_STATUSES as status (status)}
                  <button
                    type="button"
                    class="text-toggle"
                    class:active={statusFilter === status}
                    onclick={() => setStatusFilter(status)}
                  >
                    {status}
                  </button>
                {/each}
              </span>
            </div>
            <div class="filter-group">
              <span class="caption">Difficulty</span>
              <span class="toggle-row">
                <button type="button" class="text-toggle" class:active={difficultyFilter === ''} onclick={() => setDifficultyFilter('')}>all</button>
                {#each PIECE_DIFFICULTIES as d (d)}
                  <button
                    type="button"
                    class="text-toggle"
                    class:active={difficultyFilter === d}
                    onclick={() => setDifficultyFilter(d)}
                  >
                    {d}
                  </button>
                {/each}
              </span>
            </div>
            <button type="button" class="text-toggle" class:active={favoritesOnly} onclick={toggleFavoritesOnly}>
              favorites only
            </button>
          </div>
          <button type="button" class="push-right" onclick={openAddPiece}><Icon name="add" size={14} /> Add piece</button>
        {/snippet}
      </SectionHeader>

      <PieceList {pieces} onEdit={openEditPiece} onDeleted={handlePieceDeleted} onUpdated={handlePieceSaved} />
    {:else if activeView === 'focus'}
      <SectionHeader title="Focus" dek="What's actively being learned or maintained right now." />
      <RotationPlanner pieces={focusPieces} />
    {:else if activeView === 'sessions'}
      <SectionHeader title="Sessions" dek="A ledger of practice, logged session by session.">
        {#snippet actions()}
          <button type="button" class="push-right" onclick={() => (sessionModalOpen = true)}><Icon name="add" size={14} /> Log session</button>
        {/snippet}
      </SectionHeader>
      <PracticeSessionList {sessions} {pieces} />
    {:else if activeView === 'stats'}
      <SectionHeader title="Statistics" dek="Time invested, streaks kept, and pieces due for attention.">
        {#snippet actions()}
          <button type="button" class="secondary push-right" onclick={() => (goalModalOpen = true)}>
            {goal ? 'Edit goal' : 'Set goal'}
          </button>
        {/snippet}
      </SectionHeader>
      <PracticeStatsView {stats} {goal} />
    {:else if activeView === 'resources'}
      <SectionHeader title="Resources" dek="Where to find the score, part, or edition for each piece.">
        {#snippet actions()}
          <button type="button" class="push-right" onclick={() => (resourceModalOpen = true)}><Icon name="add" size={14} /> Add resource</button>
        {/snippet}
      </SectionHeader>
      <SheetResourceList resources={sheetResources} {pieces} onDeleted={handleSheetResourceDeleted} />
    {:else if activeView === 'lists'}
      <SectionHeader title="Lists" dek="Custom groupings for programs, recitals, and rotations.">
        {#snippet actions()}
          <button type="button" class="push-right" onclick={openAddList}><Icon name="add" size={14} /> New list</button>
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
    {/if}
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
  .app-shell {
    display: flex;
    min-height: 100vh;
  }

  .sidebar {
    width: 240px;
    flex: none;
    background: var(--sidebar-bg);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    transition: width 150ms ease;
  }
  .app-shell.collapsed .sidebar {
    width: 64px;
  }
  @media (prefers-reduced-motion: reduce) {
    .sidebar {
      transition: none;
    }
  }

  .masthead {
    padding: var(--space-5) var(--space-4);
    border-bottom: 1px solid var(--border);
    overflow: hidden;
  }
  .masthead h1 {
    font-size: var(--text-lg);
    white-space: nowrap;
  }
  .colophon {
    margin: var(--space-1) 0 0;
    white-space: nowrap;
  }
  .app-shell.collapsed .masthead h1,
  .app-shell.collapsed .masthead .colophon {
    display: none;
  }

  nav ul {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  nav li {
    border-bottom: 1px solid var(--border);
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    width: 100%;
    padding: var(--space-3) var(--space-4);
    background: none;
    border: none;
    color: var(--ink-soft);
    font-variant-caps: normal;
    letter-spacing: normal;
    font-weight: 400;
    text-align: left;
    cursor: pointer;
    position: relative;
  }
  .nav-item:hover:not(:disabled) {
    background: none;
    border-color: transparent;
  }
  .nav-item:hover .label {
    text-decoration: underline;
  }
  .nav-item .tick {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 1.5px;
    background: transparent;
  }
  .nav-item.active {
    color: var(--accent);
  }
  .nav-item.active .tick {
    background: var(--accent);
  }
  .label {
    font-size: var(--text-sm);
  }
  .app-shell.collapsed .nav-item {
    justify-content: center;
    padding: var(--space-3) 0;
  }
  .app-shell.collapsed .nav-item .label {
    display: none;
  }

  .sidebar-footer {
    margin-top: auto;
    border-top: 1px solid var(--border);
    padding: var(--space-3) var(--space-4);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
  }
  .rail-toggle {
    background: none;
    border: none;
    padding: var(--space-1);
    color: var(--ink-faint);
  }
  .rail-toggle:hover:not(:disabled) {
    background: none;
    border-color: transparent;
    color: var(--ink);
  }
  .health {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    overflow: hidden;
  }
  .dot {
    flex: none;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    border: 1px solid var(--ink-faint);
    background: transparent;
  }
  .dot.online {
    background: var(--ink);
    border-color: var(--ink);
  }
  .health-label {
    white-space: nowrap;
  }
  .app-shell.collapsed .health-label {
    display: none;
  }

  .content {
    flex: 1;
    min-width: 0;
    padding: var(--space-6) var(--space-6) var(--space-7);
    max-width: 56rem;
  }

  .filter-groups {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: var(--space-5);
  }
  .filter-group {
    display: flex;
    align-items: baseline;
    gap: var(--space-2);
  }
</style>
