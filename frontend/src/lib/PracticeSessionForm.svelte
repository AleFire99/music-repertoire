<script lang="ts">
  import { createPracticeSession, type Piece, type PracticeSession } from './api'

  let {
    pieces,
    onSaved,
  }: {
    pieces: Piece[]
    onSaved: (session: PracticeSession) => void
  } = $props()

  function nowLocalInputValue(): string {
    const now = new Date()
    const pad = (n: number) => String(n).padStart(2, '0')
    return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`
  }

  let pieceId = $state<number | ''>('')
  let practicedAt = $state(nowLocalInputValue())
  let durationMinutes = $state('')
  let notes = $state('')
  let rating = $state<number | ''>('')
  let section = $state('')
  let submitting = $state(false)
  let formError = $state<string | null>(null)

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
    <input type="number" bind:value={durationMinutes} min="1" required />
  </label>
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
  </div>
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }
  label {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    font-size: 0.9rem;
  }
  .actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.25rem;
  }
  .error {
    color: #b00020;
  }
</style>
