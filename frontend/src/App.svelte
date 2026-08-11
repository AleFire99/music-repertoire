<script lang="ts">
  import { onMount } from 'svelte'
  import { getHealth, listPieces, PIECE_STATUSES, type Piece, type PieceStatus } from './lib/api'

  let health = $state<string>('checking...')
  let pieces = $state<Piece[]>([])
  let error = $state<string | null>(null)
  let statusFilter = $state<PieceStatus | ''>('')

  async function refreshPieces(): Promise<void> {
    pieces = await listPieces({ status: statusFilter || undefined })
  }

  onMount(async () => {
    try {
      const healthResult = await getHealth()
      health = healthResult.status
      await refreshPieces()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  })

  async function onStatusFilterChange(): Promise<void> {
    try {
      await refreshPieces()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  }
</script>

<main>
  <h1>Music Repertoire</h1>
  <p>API health: <strong>{health}</strong></p>

  {#if error}
    <p class="error">{error}</p>
  {/if}

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

  {#if pieces.length === 0}
    <p>No pieces yet.</p>
  {:else}
    <ul>
      {#each pieces as piece (piece.id)}
        <li>
          {piece.title}{piece.composer ? ` — ${piece.composer}` : ''}
          <span class="status">{piece.status}</span>
          {#if piece.tags.length > 0}
            <span class="tags">{piece.tags.join(', ')}</span>
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
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
  .status {
    margin-left: 0.5rem;
    padding: 0.1rem 0.5rem;
    border-radius: 0.75rem;
    background: #e0e0e0;
    font-size: 0.8rem;
  }
  .tags {
    margin-left: 0.5rem;
    color: #666;
    font-size: 0.8rem;
  }
</style>
