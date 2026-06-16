<script lang="ts">
  export let title: string;
  export let value: string;
  export let subtitle: string = '';
</script>

<div class="card p-5">
  <div class="text-sm font-medium text-slate-500">{title}</div>
  <div class="mt-3 text-2xl font-semibold text-slate-900">{value}</div>
  {#if subtitle}
    <div class="mt-1 text-sm text-slate-500">{subtitle}</div>
  {/if}
</div>
