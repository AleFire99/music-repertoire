<script lang="ts">
  import { onDestroy } from 'svelte'
  import { createPracticeSession, type Piece, type PracticeSession } from './api'

  let {
    pieces,
    onSaved,
    onCancel,
  }: {
    pieces: Piece[]
    onSaved: (session: PracticeSession) => void
    onCancel?: () => void
  } = $props()

  function nowLocalInputValue(): string {
    const now = new Date()
    const pad = (n: number) => String(n).padStart(2, '0')
    return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`
  }

  function formatElapsed(totalSeconds: number): string {
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  }

  let pieceId = $state<number | ''>('')
  let practicedAt = $state(nowLocalInputValue())
  let durationMinutes = $state('')
  let notes = $state('')
  let rating = $state<number | ''>('')
  let section = $state('')
  let submitting = $state(false)
  let formError = $state<string | null>(null)

  let timerRunning = $state(false)
  let elapsedSeconds = $state(0)
  let timerStartedAt: number | null = null
  let timerHandle: ReturnType<typeof setInterval> | null = null

  function startTimer(): void {
    if (timerRunning) return
    timerRunning = true
    timerStartedAt = Date.now() - elapsedSeconds * 1000
    timerHandle = setInterval(() => {
      elapsedSeconds = Math.floor((Date.now() - timerStartedAt!) / 1000)
    }, 1000)
  }

  function stopTimer(): void {
    if (!timerRunning) return
    timerRunning = false
    if (timerHandle !== null) clearInterval(timerHandle)
    timerHandle = null
    durationMinutes = String(Math.max(1, Math.round(elapsedSeconds / 60)))
  }

  function resetTimer(): void {
    if (timerHandle !== null) clearInterval(timerHandle)
    timerHandle = null
    timerRunning = false
    elapsedSeconds = 0
    timerStartedAt = null
  }

  onDestroy(() => {
    if (timerHandle !== null) clearInterval(timerHandle)
  })

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    submitting = true
    formError = null
    try {
      const payload = {
        piece_id: Number(pieceId),
        practiced_at: new Date(practicedAt).toISOString(),
        duration_minutes: Number(durationMinutes),
        notes: notes.trim() || null,
        rating: rating === '' ? null : Number(rating),
        section: section.trim() || null,
      }
      const saved = await createPracticeSession(payload)
      onSaved(saved)
      practicedAt = nowLocalInputValue()
      durationMinutes = ''
      notes = ''
      rating = ''
      section = ''
    } catch (err) {
      formError = err instanceof Error ? err.message : String(err)
    } finally {
      submitting = false
    }
  }
</script>

<form onsubmit={handleSubmit}>
  <label>
    Piece
    <select bind:value={pieceId} required>
      <option value="" disabled>Select a piece…</option>
      {#each pieces as piece (piece.id)}
        <option value={piece.id}>{piece.title}</option>
      {/each}
    </select>
  </label>
  <label>
    Date &amp; time
    <input type="datetime-local" bind:value={practicedAt} required />
  </label>
  <label>
    Duration (minutes)
    <input type="text" inputmode="numeric" bind:value={durationMinutes} min="1" required />
  </label>
  <div class="timer">
    <span class="readout readout-lg timer-display">{formatElapsed(elapsedSeconds)}</span>
    <button type="button" class="secondary" onclick={startTimer} disabled={timerRunning}>Start</button>
    <button type="button" class="secondary" onclick={stopTimer} disabled={!timerRunning}>Stop</button>
    <button type="button" class="secondary" onclick={resetTimer} disabled={timerRunning}>Reset</button>
  </div>
  <label>
    Section (optional)
    <input type="text" bind:value={section} maxlength="200" placeholder="measures 1-16" />
  </label>
  <label>
    Rating (optional)
    <select bind:value={rating}>
      <option value="">No rating</option>
      {#each [1, 2, 3, 4, 5] as r (r)}
        <option value={r}>{r}</option>
      {/each}
    </select>
  </label>
  <label>
    Notes (optional)
    <textarea bind:value={notes} maxlength="2000" rows="3"></textarea>
  </label>

  {#if formError}
    <p class="error">{formError}</p>
  {/if}

  <div class="actions">
    <button type="submit" disabled={submitting || pieceId === ''}>
      {submitting ? 'Saving…' : 'Log Session'}
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
  .timer {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-3);
    background: var(--surface-hover);
    border-radius: var(--radius-sm);
  }
  .timer-display {
    min-width: 3.5ch;
  }
</style>
