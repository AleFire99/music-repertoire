<script lang="ts">
  import {
    createPiece,
    updatePiece,
    PIECE_STATUSES,
    PIECE_DIFFICULTIES,
    type Piece,
    type PieceStatus,
    type PieceDifficulty,
  } from './api'

  let {
    piece = null,
    onSaved,
    onCancel,
  }: {
    piece?: Piece | null
    onSaved: (piece: Piece) => void
    onCancel?: () => void
  } = $props()

  let title = $state('')
  let composer = $state('')
  let key = $state('')
  let tempoBpmRaw = $state('')
  let difficulty = $state<PieceDifficulty | ''>('')
  let instrument = $state('')
  let goalText = $state('')
  let goalTargetDate = $state('')
  let status = $state<PieceStatus>('backlog')
  let tagsRaw = $state('')
  let submitting = $state(false)
  let formError = $state<string | null>(null)

  $effect(() => {
    title = piece?.title ?? ''
    composer = piece?.composer ?? ''
    key = piece?.key ?? ''
    tempoBpmRaw = piece?.tempo_bpm != null ? String(piece.tempo_bpm) : ''
    difficulty = piece?.difficulty ?? ''
    instrument = piece?.instrument ?? ''
    goalText = piece?.goal_text ?? ''
    goalTargetDate = piece?.goal_target_date ?? ''
    status = piece?.status ?? 'backlog'
    tagsRaw = piece?.tags.join(', ') ?? ''
    formError = null
  })

  function parseTags(raw: string): string[] {
    return raw
      .split(',')
      .map((t) => t.trim())
      .filter((t) => t.length > 0)
      .map((t) => (t.length > 50 ? t.slice(0, 50) : t))
  }

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    submitting = true
    formError = null
    try {
      const tempoBpmParsed = tempoBpmRaw.trim() === '' ? null : Number(tempoBpmRaw.trim())
      const payload = {
        title: title.trim(),
        composer: composer.trim() || null,
        key: key.trim() || null,
        tempo_bpm: tempoBpmParsed != null && Number.isNaN(tempoBpmParsed) ? null : tempoBpmParsed,
        difficulty: difficulty || null,
        instrument: instrument.trim() || null,
        goal_text: goalText.trim() || null,
        goal_target_date: goalTargetDate.trim() || null,
        status,
        tags: parseTags(tagsRaw),
      }
      const saved = piece ? await updatePiece(piece.id, payload) : await createPiece(payload)
      onSaved(saved)
    } catch (err) {
      formError = err instanceof Error ? err.message : String(err)
    } finally {
      submitting = false
    }
  }
</script>

<form onsubmit={handleSubmit}>
  <label>
    Title
    <input type="text" bind:value={title} required maxlength="200" />
  </label>
  <label>
    Composer
    <input type="text" bind:value={composer} maxlength="200" />
  </label>
  <label>
    Key
    <input type="text" bind:value={key} maxlength="50" />
  </label>
  <label>
    Tempo (BPM)
    <input type="number" min="1" bind:value={tempoBpmRaw} />
  </label>
  <label>
    Difficulty
    <select bind:value={difficulty}>
      <option value="">Unset</option>
      {#each PIECE_DIFFICULTIES as d (d)}
        <option value={d}>{d}</option>
      {/each}
    </select>
  </label>
  <label>
    Instrument
    <input type="text" bind:value={instrument} maxlength="100" />
  </label>
  <label>
    Goal
    <input
      type="text"
      bind:value={goalText}
      maxlength="500"
      placeholder="performance-ready for the June recital"
    />
  </label>
  <label>
    Goal target date
    <input type="date" bind:value={goalTargetDate} />
  </label>
  <label>
    Status
    <select bind:value={status}>
      {#each PIECE_STATUSES as s (s)}
        <option value={s}>{s}</option>
      {/each}
    </select>
  </label>
  <label>
    Tags (comma-separated)
    <input type="text" bind:value={tagsRaw} placeholder="jazz, sight-reading" />
  </label>

  {#if formError}
    <p class="error">{formError}</p>
  {/if}

  <div class="actions">
    <button type="submit" disabled={submitting}>
      {#if submitting}Saving…{:else}{piece ? 'Save' : 'Add Piece'}{/if}
    </button>
    <button type="button" class="secondary" onclick={onCancel} disabled={submitting}>Cancel</button>
  </div>
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }
</style>
