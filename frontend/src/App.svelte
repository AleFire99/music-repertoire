<script lang="ts">
  import { onMount } from 'svelte'
  import { getHealth, listPieces, type Piece } from './lib/api'

  let health = $state<string>('checking...')
  let pieces = $state<Piece[]>([])
  let error = $state<string | null>(null)

  onMount(async () => {
    try {
      const healthResult = await getHealth()
      health = healthResult.status
      pieces = await listPieces()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  })
</script>

<main>
  <h1>Music Repertoire</h1>
  <p>API health: <strong>{health}</strong></p>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <h2>Pieces</h2>
  {#if pieces.length === 0}
    <p>No pieces yet.</p>
  {:else}
    <ul>
      {#each pieces as piece (piece.id)}
        <li>{piece.title}{piece.composer ? ` — ${piece.composer}` : ''}</li>
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
</style>
