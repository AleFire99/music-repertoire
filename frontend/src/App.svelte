<script lang="ts">
  import { onMount } from 'svelte'
  import {
    getHealth,
    getPracticeGoal,
    getPracticeStats,
    listPieces,
    listPracticeSessions,
    listRepertoireLists,
    PIECE_STATUSES,
    PIECE_DIFFICULTIES,
    type Piece,
    type PieceStatus,
    type PieceDifficulty,
    type PracticeGoal,
    type PracticeSession,
    type PracticeStats,
    type RepertoireList,
  } from './lib/api'
  import Icon from './lib/Icon.svelte'
  import Modal from './lib/Modal.svelte'
  import PieceForm from './lib/PieceForm.svelte'
  import PieceGrid from './lib/PieceGrid.svelte'
  import PieceList from './lib/PieceList.svelte'
  import PracticeGoalForm from './lib/PracticeGoalForm.svelte'
  import PracticeSessionForm from './lib/PracticeSessionForm.svelte'
  import PracticeSessionList from './lib/PracticeSessionList.svelte'
  import PracticeStatsView from './lib/PracticeStats.svelte'
  import QuickUploadPieceForm from './lib/QuickUploadPieceForm.svelte'
  import RepertoireListForm from './lib/RepertoireListForm.svelte'
  import RepertoireListList from './lib/RepertoireListList.svelte'
  import RotationPlanner from './lib/RotationPlanner.svelte'
  import SectionHeader from './lib/SectionHeader.svelte'

  type ViewId = 'pieces' | 'focus' | 'sessions' | 'stats' | 'lists'

  const NAV_GROUPS: { label: string; items: { id: ViewId; label: string; icon: string }[] }[] = [
    {
      label: 'Practice',
      items: [
        { id: 'focus', label: 'Today & Focus', icon: 'focus' },
        { id: 'sessions', label: 'Sessions', icon: 'sessions' },
        { id: 'stats', label: 'Progress', icon: 'stats' },
      ],
    },
    {
      label: 'Library',
      items: [
        { id: 'pieces', label: 'Pieces', icon: 'pieces' },
        { id: 'lists', label: 'Lists', icon: 'list' },
      ],
    },
  ]

  type Theme = 'light' | 'dark'

  function preferredTheme(): Theme {
    const stored = localStorage.getItem('theme')
    if (stored === 'light' || stored === 'dark') return stored
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  const initialTheme = preferredTheme()
  let theme = $state<Theme>(initialTheme)

  function applyTheme(next: Theme): void {
    document.documentElement.setAttribute('data-theme', next)
  }

  function toggleTheme(): void {
    theme = theme === 'dark' ? 'light' : 'dark'
    localStorage.setItem('theme', theme)
    applyTheme(theme)
  }

  applyTheme(initialTheme)

  let activeView = $state<ViewId>('focus')
  let sidebarCollapsed = $state(localStorage.getItem('sidebar-collapsed') === 'true')

  function toggleSidebar(): void {
    sidebarCollapsed = !sidebarCollapsed
    localStorage.setItem('sidebar-collapsed', String(sidebarCollapsed))
  }

  type PieceViewMode = 'table' | 'grid'

  function storedPieceViewMode(): PieceViewMode {
    const stored = localStorage.getItem('pieces-view-mode')
    return stored === 'grid' ? 'grid' : 'table'
  }

  let pieceViewMode = $state<PieceViewMode>(storedPieceViewMode())

  function setPieceViewMode(mode: PieceViewMode): void {
    pieceViewMode = mode
    localStorage.setItem('pieces-view-mode', mode)
  }

  let health = $state<string>('checking...')
  let pieces = $state<Piece[]>([])
  let error = $state<string | null>(null)
  let statusFilter = $state<PieceStatus | ''>('')
  let favoritesOnly = $state<boolean>(false)
  let difficultyFilter = $state<PieceDifficulty | ''>('')
  let pieceQuery = $state('')
  let editingPiece = $state<Piece | null>(null)
  let pieceModalOpen = $state(false)
  let quickUploadModalOpen = $state(false)
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
    consistency_heatmap: [],
    suggested_plan: [],
  })
  let goal = $state<PracticeGoal | null>(null)
  let goalModalOpen = $state(false)
  let repertoireLists = $state<RepertoireList[]>([])
  let editingRepertoireList = $state<RepertoireList | null>(null)
  let listModalOpen = $state(false)
  let focusPieces = $state<Piece[]>([])

  const filteredPieces = $derived(
    pieceQuery.trim() === ''
      ? pieces
      : pieces.filter((p) =>
          `${p.title} ${p.composer ?? ''} ${p.key ?? ''} ${p.tags.join(' ')}`
            .toLowerCase()
            .includes(pieceQuery.trim().toLowerCase()),
        ),
  )

  const weekGoalPct = $derived(
    goal ? Math.min(100, Math.round((goal.minutes_this_week / goal.target_minutes) * 100)) : 0,
  )

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

  function handleQuickUploadSuccess(piece: Piece): void {
    const exists = pieces.some((p) => p.id === piece.id)
    pieces = exists ? pieces.map((p) => (p.id === piece.id ? piece : p)) : [...pieces, piece]
    quickUploadModalOpen = false
    refreshFocusPieces().catch((err) => {
      error = err instanceof Error ? err.message : String(err)
    })
    openEditPiece(piece)
  }

  function handlePieceDeleted(id: number): void {
    pieces = pieces.filter((p) => p.id !== id)
    if (editingPiece?.id === id) closePieceModal()
    refreshRepertoireLists().catch((err) => {
      error = err instanceof Error ? err.message : String(err)
    })
    refreshFocusPieces().catch((err) => {
      error = err instanceof Error ? err.message : String(err)
    })
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
      <div class="brand">
        <Icon name="brand" size={20} />
        <span class="brand-name">Music Repertoire</span>
      </div>
      <p class="colophon caption">{pieces.length} piece{pieces.length === 1 ? '' : 's'} catalogued</p>
    </div>

    <nav>
      {#each NAV_GROUPS as group (group.label)}
        <div class="nav-group-label caption">{group.label}</div>
        <ul>
          {#each group.items as item (item.id)}
            <li>
              <button
                type="button"
                class="nav-item"
                class:active={activeView === item.id}
                onclick={() => (activeView = item.id)}
                title={item.label}
              >
                <Icon name={item.icon} size={18} />
                <span class="label">{item.label}</span>
              </button>
            </li>
          {/each}
        </ul>
      {/each}
    </nav>

    <div class="sidebar-footer">
      {#if goal}
        <div class="goal-mini">
          <div class="goal-mini-row">
            <span class="caption">This week</span>
            <span class="goal-mini-value">{goal.minutes_this_week}m / {goal.target_minutes}m</span>
          </div>
          <div class="goal-mini-track">
            <div class="goal-mini-fill" style="width: {weekGoalPct}%"></div>
          </div>
        </div>
      {:else}
        <button type="button" class="goal-mini-empty caption" onclick={() => (goalModalOpen = true)}>
          Set a weekly goal
        </button>
      {/if}

      <button type="button" class="primary start-session" onclick={() => (sessionModalOpen = true)}>
        <Icon name="play" size={16} />
        <span class="label">Start a session</span>
      </button>

      <button type="button" class="theme-toggle" onclick={toggleTheme}>
        <Icon name={theme === 'dark' ? 'theme-sun' : 'theme-moon'} size={15} />
        <span class="label">{theme === 'dark' ? 'Light theme' : 'Dark theme'}</span>
      </button>

      <div class="footer-row">
        <button
          type="button"
          class="rail-toggle"
          onclick={toggleSidebar}
          aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <Icon name="sidebar-toggle" size={17} />
        </button>
        <div class="health">
          <span class="dot" class:online={health === 'ok'} aria-hidden="true"></span>
          <span class="health-label caption">{health === 'ok' ? 'connected' : 'offline'}</span>
        </div>
      </div>
    </div>
  </aside>

  <main class="content">
    {#if error}
      <p class="error">{error}</p>
    {/if}

    {#if activeView === 'pieces'}
      <SectionHeader
        kicker="Your library"
        title="Pieces"
        subtitle="Standards, soundtracks, contemporary and your own writing, each catalogued with its status and goal."
      >
        {#snippet actions()}
          <label class="search-field">
            <Icon name="search" size={15} />
            <input
              type="search"
              placeholder="Search title, composer, key"
              bind:value={pieceQuery}
            />
          </label>
          <div class="view-toggle" role="group" aria-label="Pieces view">
            <button
              type="button"
              class="view-toggle-btn"
              class:active={pieceViewMode === 'table'}
              onclick={() => setPieceViewMode('table')}
              aria-label="Table view"
              aria-pressed={pieceViewMode === 'table'}
            >
              <Icon name="view-table" size={16} />
            </button>
            <button
              type="button"
              class="view-toggle-btn"
              class:active={pieceViewMode === 'grid'}
              onclick={() => setPieceViewMode('grid')}
              aria-label="Grid view"
              aria-pressed={pieceViewMode === 'grid'}
            >
              <Icon name="view-grid" size={16} />
            </button>
          </div>
          <button type="button" class="secondary" onclick={() => (quickUploadModalOpen = true)}>
            <Icon name="upload" size={14} /> Upload PDF
          </button>
          <button type="button" onclick={openAddPiece}><Icon name="add" size={14} /> Add piece</button>
        {/snippet}
      </SectionHeader>

      <div class="filter-groups">
        <label class="filter-field">
          Status
          <select
            value={statusFilter}
            onchange={(e) => setStatusFilter(e.currentTarget.value as PieceStatus | '')}
          >
            <option value="">All</option>
            {#each PIECE_STATUSES as status (status)}
              <option value={status}>{status}</option>
            {/each}
          </select>
        </label>
        <label class="filter-field">
          Difficulty
          <select
            value={difficultyFilter}
            onchange={(e) => setDifficultyFilter(e.currentTarget.value as PieceDifficulty | '')}
          >
            <option value="">All difficulties</option>
            {#each PIECE_DIFFICULTIES as d (d)}
              <option value={d}>{d}</option>
            {/each}
          </select>
        </label>
        <button type="button" class="text-toggle" class:active={favoritesOnly} onclick={toggleFavoritesOnly}>
          favorites only
        </button>
      </div>

      {#if pieceViewMode === 'grid'}
        <PieceGrid pieces={filteredPieces} />
      {:else}
        <PieceList pieces={filteredPieces} stats={stats.pieces} onEdit={openEditPiece} onDeleted={handlePieceDeleted} onUpdated={handlePieceSaved} />
      {/if}
    {:else if activeView === 'focus'}
      <SectionHeader kicker="Right now" title="Today & Focus" subtitle="A plan for the next hour, and what you're actively carrying." />
      <RotationPlanner pieces={focusPieces} suggestedPlan={stats.suggested_plan} onStartSession={() => (sessionModalOpen = true)} onAddPiece={openAddPiece} />
    {:else if activeView === 'sessions'}
      <SectionHeader kicker="Practice log" title="Sessions" subtitle="A ledger of practice, logged session by session.">
        {#snippet actions()}
          <button type="button" onclick={() => (sessionModalOpen = true)}><Icon name="add" size={14} /> Log session</button>
        {/snippet}
      </SectionHeader>
      <PracticeSessionList {sessions} {pieces} />
    {:else if activeView === 'stats'}
      <SectionHeader kicker="How it's going" title="Progress" subtitle="Time invested, streaks kept, and pieces due for attention.">
        {#snippet actions()}
          <button type="button" class="secondary" onclick={() => (goalModalOpen = true)}>
            {goal ? 'Edit goal' : 'Set goal'}
          </button>
        {/snippet}
      </SectionHeader>
      <PracticeStatsView {stats} {goal} />
    {:else if activeView === 'lists'}
      <SectionHeader kicker="Groupings" title="Lists" subtitle="Custom groupings for programs, recitals, and rotations.">
        {#snippet actions()}
          <button type="button" onclick={openAddList}><Icon name="add" size={14} /> New list</button>
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

<Modal open={pieceModalOpen} title={editingPiece ? 'Edit piece' : 'Add piece'} size="large" onClose={closePieceModal}>
  <PieceForm piece={editingPiece} onSaved={handlePieceSaved} onCancel={closePieceModal} />
</Modal>

<Modal open={quickUploadModalOpen} title="Upload PDF" size="small" onClose={() => (quickUploadModalOpen = false)}>
  <QuickUploadPieceForm onUploaded={handleQuickUploadSuccess} onCancel={() => (quickUploadModalOpen = false)} />
</Modal>

<Modal open={sessionModalOpen} title="Log practice session" onClose={() => (sessionModalOpen = false)}>
  <PracticeSessionForm {pieces} onSaved={handleSessionSaved} onCancel={() => (sessionModalOpen = false)} />
</Modal>

<Modal open={goalModalOpen} title={goal ? 'Edit weekly goal' : 'Set weekly goal'} size="small" onClose={() => (goalModalOpen = false)}>
  <PracticeGoalForm {goal} onSaved={handleGoalSaved} onCancel={() => (goalModalOpen = false)} />
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
    width: 256px;
    flex: none;
    background: var(--surface);
    border-right: var(--border-width-strong) solid var(--border);
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
    border-bottom: var(--border-width-strong) solid var(--border);
    overflow: hidden;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--accent);
  }
  .brand-name {
    font-family: var(--font-heading);
    font-weight: var(--font-heading-weight);
    font-size: var(--text-md);
    color: var(--ink);
    letter-spacing: -0.01em;
    white-space: nowrap;
  }
  .colophon {
    margin: var(--space-2) 0 0;
    white-space: nowrap;
  }
  .app-shell.collapsed .masthead .brand-name,
  .app-shell.collapsed .masthead .colophon {
    display: none;
  }

  nav {
    display: flex;
    flex-direction: column;
    padding: var(--space-3) var(--space-2) var(--space-2);
    gap: 2px;
  }
  nav ul {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .nav-group-label {
    padding: var(--space-2) var(--space-3) var(--space-1);
  }
  .app-shell.collapsed .nav-group-label {
    display: none;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    width: 100%;
    padding: var(--space-2) var(--space-3);
    background: none;
    border: none;
    border-radius: var(--radius-full);
    color: var(--ink);
    font-family: var(--font-body);
    font-weight: 400;
    font-size: var(--text-sm);
    text-align: left;
    cursor: pointer;
  }
  .nav-item:hover:not(:disabled) {
    background: color-mix(in srgb, var(--ink) calc(var(--state-hover) * 100%), transparent);
  }
  .nav-item.active {
    background: var(--accent-100);
    color: var(--accent-700);
    font-family: var(--font-heading);
    font-weight: var(--font-heading-weight);
  }
  .nav-item.active:hover:not(:disabled) {
    background: var(--accent-200);
  }
  .label {
    white-space: nowrap;
  }
  .app-shell.collapsed .nav-item {
    justify-content: center;
    padding: var(--space-2) 0;
  }
  .app-shell.collapsed .nav-item .label {
    display: none;
  }

  .sidebar-footer {
    margin-top: auto;
    border-top: var(--border-width-strong) solid var(--border);
    padding: var(--space-4);
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }
  .app-shell.collapsed .sidebar-footer {
    padding: var(--space-3) var(--space-2);
  }
  .app-shell.collapsed .goal-mini,
  .app-shell.collapsed .goal-mini-empty,
  .app-shell.collapsed .start-session .label,
  .app-shell.collapsed .theme-toggle .label {
    display: none;
  }

  .goal-mini-row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: var(--space-2);
  }
  .goal-mini-value {
    font-family: var(--font-heading);
    font-weight: var(--font-heading-weight);
    font-size: var(--text-sm);
  }
  .goal-mini-track {
    height: 6px;
    background: var(--border);
  }
  .goal-mini-fill {
    height: 100%;
    background: var(--accent);
  }
  .goal-mini-empty {
    margin: 0;
    padding: 0;
    background: none;
    border: none;
    border-radius: 0;
    color: var(--ink-faint);
    text-align: left;
    text-decoration: underline;
    text-decoration-color: var(--outline);
    text-underline-offset: 2px;
  }
  .goal-mini-empty:hover:not(:disabled) {
    background: none;
    color: var(--accent);
    text-decoration-color: currentColor;
  }

  .start-session {
    width: 100%;
    justify-content: flex-start;
  }

  .theme-toggle {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    width: 100%;
    padding: var(--space-1) 0;
    background: transparent;
    color: var(--ink-soft);
    border: none;
    font-size: var(--text-xs);
    font-family: var(--font-body);
    font-weight: 400;
  }
  .theme-toggle:hover:not(:disabled) {
    background: none;
    color: var(--ink);
  }
  .app-shell.collapsed .theme-toggle {
    justify-content: center;
  }

  .footer-row {
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
    width: 8px;
    height: 8px;
    border-radius: var(--radius-full);
    background: var(--ink-faint);
    box-shadow: 0 0 0 0 transparent;
    transition: background 200ms ease, box-shadow 200ms ease;
  }
  .dot.online {
    background: var(--accent);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 22%, transparent);
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
    padding: var(--space-6) var(--space-7) var(--space-7);
  }

  .filter-groups {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-4);
    margin-bottom: var(--space-5);
  }

  .filter-field {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-sm);
    color: var(--ink-soft);
  }

  .search-field {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    background: var(--surface-container-low);
    border: var(--border-width) solid var(--outline);
    border-radius: var(--radius-full);
    padding: 0 var(--space-4);
    height: 36px;
    width: 18rem;
    color: var(--ink-faint);
  }
  .search-field input {
    flex: 1;
    min-width: 0;
    width: 100%;
    border: 0;
    padding: 0;
    background: transparent;
    color: var(--ink);
    font-size: var(--text-sm);
    text-overflow: ellipsis;
  }
  .search-field input:focus-visible {
    outline: none;
    box-shadow: none;
  }

  .view-toggle {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    padding: 2px;
    background: var(--surface-container);
    border-radius: var(--radius-full);
  }
  .view-toggle-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    padding: 0;
    background: none;
    border: none;
    border-radius: var(--radius-full);
    color: var(--ink-faint);
  }
  .view-toggle-btn:hover:not(:disabled) {
    background: color-mix(in srgb, var(--ink) calc(var(--state-hover) * 100%), transparent);
    color: var(--ink);
  }
  .view-toggle-btn.active {
    background: var(--accent-100);
    color: var(--accent-700);
  }
  .view-toggle-btn.active:hover:not(:disabled) {
    background: var(--accent-200);
  }
</style>
