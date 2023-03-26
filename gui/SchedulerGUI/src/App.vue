<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <DynamicDialog />
  <div class="container m-auto grid grid-cols-3">
    <nav>
      <ul>
        <li><RouterLink to="/">Hem</RouterLink></li>
        <li><RouterLink to="om">Om</RouterLink></li>
      </ul>
    </nav>
  </div>
  <div class="container m-auto grid grid-cols-1">
    <RouterView />
  </div>
  
</template>