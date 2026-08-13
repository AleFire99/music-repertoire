<script lang="ts">
  let { name, size = 20 }: { name: string; size?: number } = $props()
</script>

<svg width={size} height={size} viewBox="0 0 20 20" aria-hidden="true" focusable="false"
  ><use href={`/icons.svg#${name}`} /></svg>

<style>
  svg {
    display: inline-block;
    flex: none;
    vertical-align: middle;
  }
</style>
